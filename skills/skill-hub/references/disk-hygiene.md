# Disk hygiene for agent work

Keep temporary storage bounded during every task. Put scratch files, intermediate renders, test captures, downloaded inputs, and generated build experiments in a task-specific temporary directory when practical. Track the paths you create.

Before finishing a task, move requested deliverables to their intended location, then remove the task's disposable files and temporary directory. Clean up after failed or interrupted work when possible. For long tasks, remove superseded intermediates as you go. Check the size of unusually large scratch output before leaving it behind.

Delete only files you created for this task and know are disposable. Do not sweep a shared temp directory or delete pre-existing files, another process's files, user data, conversation history, dependencies, caches shared across tasks, or final deliverables. If an output's value is unclear, preserve it and tell the user its path and size. If permissions or a running process prevent cleanup, report the leftover path and size.
