---
name: debugging
type: mode-shift
description: >
  Use this skill to help debug issues with the agent. It can be invoked by the agent itself or by a user. The skill can be used to inspect the agent's state, check for errors, and provide suggestions for fixing issues.
model-invocable: true
---

# Exploration Skills

How to explore the codebase and debug issues with the agent.
Finding the right files and understanding the code structure is crucial for effective debugging. This skill provides guidance on how to navigate the codebase, identify relevant files, and understand their purpose.

# Known python issues

Here are some known issues with the Python codebase that you may encounter while debugging:

- **Issue 1: Incorrect import statements**
  - **Description:** Some files may have incorrect or missing import statements, leading to `ModuleNotFoundError` or `ImportError`.
  - **Solution:** Check the import statements in the relevant files and ensure that all necessary modules are imported correctly. Use absolute imports where possible.
- **Issue 2: Circular imports**
  - **Description:** Circular imports can occur when two or more modules depend on each other, leading to `ImportError`.
  - **Solution:** Refactor the code to eliminate circular dependencies. Consider using local imports or restructuring the code to avoid circular references.
- **Issue 3: Deprecated functions or libraries**
  - **Description:** Some functions or libraries used in the codebase may be deprecated, leading to warnings or errors.
  - **Solution:** Update the code to use the latest functions or libraries. Check the documentation for any changes in function signatures or behavior.
- **Issue 4: Incorrect file paths**
  - **Description:** File paths may be incorrect or not properly configured, leading to `FileNotFoundError`.
  - **Solution:** Verify the file paths in the code and ensure that they are correct. Use relative paths where appropriate and check for typos in file names.
- **Issue 5: Syntax errors**
  - **Description:** Syntax errors can occur due to typos or incorrect code structure, leading to `SyntaxError`.
  - **Solution:** Review the code for any syntax errors and correct them. Use a linter or code editor with syntax highlighting to catch errors early.
- **Issue 6: Unhandled exceptions**
  - **Description:** Some parts of the code may not handle exceptions properly, leading to crashes or unexpected behavior.
  - **Solution:** Implement proper exception handling using try-except blocks. Log errors and provide meaningful error messages to aid in debugging.
- **Issue 7: Inconsistent variable naming**
  - **Description:** Inconsistent variable naming can lead to confusion and make the code harder to read and maintain.
  - **Solution:** Follow a consistent naming convention for variables, functions, and classes. Use descriptive names that convey the purpose of the variable or function.
- Division by zero errors
  - **Description:** Division by zero can occur in mathematical operations, leading to `ZeroDivisionError`.
  - **Solution:** Check for potential division by zero scenarios and implement checks to prevent it. Use conditional statements to handle cases where the denominator may be zero.
