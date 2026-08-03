"""MongoDB-backed storage for Claude Agent SDK sessions."""

import os
import time

from claude_agent_sdk import (
    SessionKey,
    SessionListSubkeysKey,
    SessionStoreEntry,
    SessionStoreListEntry,
    SessionSummaryEntry,
    fold_session_summary,
)
from pymongo import ASCENDING, AsyncMongoClient, ReturnDocument


class CustomSessionStore:
    """Persist Claude SDK session transcripts in MongoDB.

    Transcript batches are separate documents, so long-lived sessions do not
    hit MongoDB's 16 MB document limit.
    """

    def __init__(
        self,
        uri: str | None = None,
        database: str | None = None,
    ) -> None:
        self._client = AsyncMongoClient(
            uri or os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
        )
        db = self._client[
            database or os.environ.get("MONGODB_DATABASE", "claude_sessions")
        ]
        self._sessions = db["sessions"]
        self._batches = db["transcript_batches"]
        self._summaries = db["summaries"]
        self._indexes_ready = False

    async def _ensure_indexes(self) -> None:
        if self._indexes_ready:
            return
        await self._sessions.create_index(
            [
                ("project_key", ASCENDING),
                ("session_id", ASCENDING),
                ("subpath", ASCENDING),
            ],
            unique=True,
        )
        await self._sessions.create_index(
            [("project_key", ASCENDING), ("subpath", ASCENDING), ("mtime", ASCENDING)]
        )
        await self._batches.create_index(
            [
                ("project_key", ASCENDING),
                ("session_id", ASCENDING),
                ("subpath", ASCENDING),
                ("sequence", ASCENDING),
            ],
            unique=True,
        )
        await self._summaries.create_index(
            [("project_key", ASCENDING), ("session_id", ASCENDING)], unique=True
        )
        self._indexes_ready = True

    @staticmethod
    def _filter(key: SessionKey) -> dict[str, str | None]:
        return {
            "project_key": key["project_key"],
            "session_id": key["session_id"],
            "subpath": key.get("subpath"),
        }

    @staticmethod
    def _mtime() -> int:
        return int(time.time() * 1000)

    async def append(self, key: SessionKey, entries: list[SessionStoreEntry]) -> None:
        await self._ensure_indexes()
        now_ms = self._mtime()
        transcript_filter = self._filter(key)

        transcript = await self._sessions.find_one_and_update(
            transcript_filter,
            {
                "$setOnInsert": transcript_filter,
                "$set": {"mtime": now_ms},
                "$inc": {"next_sequence": 1},
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        await self._batches.insert_one(
            {
                **transcript_filter,
                "sequence": transcript["next_sequence"],
                "entries": entries,
            }
        )

        # Summaries track only the main transcript; subagent transcripts are
        # returned separately by list_subkeys().
        if key.get("subpath") is not None:
            return

        summary_filter = {
            "project_key": key["project_key"],
            "session_id": key["session_id"],
        }
        previous = await self._summaries.find_one(summary_filter)
        previous_summary: SessionSummaryEntry | None = None
        if previous is not None:
            previous_summary = {
                "session_id": previous["session_id"],
                "mtime": previous["mtime"],
                "data": previous["data"],
            }
        summary = fold_session_summary(previous_summary, key, entries)
        summary["mtime"] = now_ms
        await self._summaries.update_one(
            summary_filter,
            {
                "$set": {"mtime": summary["mtime"], "data": summary["data"]},
                "$setOnInsert": summary_filter,
            },
            upsert=True,
        )

    async def load(self, key: SessionKey) -> list[SessionStoreEntry] | None:
        await self._ensure_indexes()
        transcript = await self._sessions.find_one(self._filter(key), {"_id": True})
        if transcript is None:
            return None
        cursor = self._batches.find(
            self._filter(key), {"_id": False, "entries": True}
        ).sort("sequence", ASCENDING)
        entries: list[SessionStoreEntry] = []
        async for batch in cursor:
            entries.extend(batch["entries"])
        return entries

    async def list_sessions(self, project_key: str) -> list[SessionStoreListEntry]:
        await self._ensure_indexes()
        cursor = self._sessions.find(
            {"project_key": project_key, "subpath": None},
            {"_id": False, "session_id": True, "mtime": True},
        )
        return [
            {"session_id": transcript["session_id"], "mtime": transcript["mtime"]}
            async for transcript in cursor
        ]

    async def list_session_summaries(
        self, project_key: str
    ) -> list[SessionSummaryEntry]:
        await self._ensure_indexes()
        cursor = self._summaries.find({"project_key": project_key}, {"_id": False})
        return [
            {
                "session_id": summary["session_id"],
                "mtime": summary["mtime"],
                "data": summary["data"],
            }
            async for summary in cursor
        ]

    async def delete(self, key: SessionKey) -> None:
        await self._ensure_indexes()
        if key.get("subpath") is not None:
            await self._sessions.delete_one(self._filter(key))
            await self._batches.delete_many(self._filter(key))
            return

        # Deleting the main transcript must cascade to every sidecar and
        # subagent transcript, and remove the corresponding summary.
        session_filter = {
            "project_key": key["project_key"],
            "session_id": key["session_id"],
        }

        await self._sessions.delete_many(session_filter)
        await self._batches.delete_many(session_filter)
        await self._summaries.delete_one(session_filter)

    async def list_subkeys(self, key: SessionListSubkeysKey) -> list[str]:
        await self._ensure_indexes()
        cursor = self._sessions.find(
            {
                "project_key": key["project_key"],
                "session_id": key["session_id"],
                "subpath": {"$ne": None},
            },
            {"_id": False, "subpath": True},
        )
        return [transcript["subpath"] async for transcript in cursor]

    async def close(self) -> None:
        """Close the MongoDB client when the application shuts down."""
        await self._client.close()
