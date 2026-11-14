# Tool and token economy

Use commands and tools to answer a concrete question or complete a required action. Prefer the smallest useful scope and output: search relevant paths, request only needed fields or lines, and cap verbose output. Avoid broad recursive scans, large shell pipelines, and commands that dump whole files when a targeted read will do.

Do not repeatedly run the same command, poll without a reason, or rerun broad tests and builds after the relevant risk is resolved. Reuse results already obtained. Batch independent checks when that reduces calls without making output harder to inspect.

Run a large or expensive command when it is genuinely needed to finish or verify the task. Keep its output bounded where practical, and stop optional checking once the result is sufficiently verified. Do not sacrifice correctness or required tests merely to save tokens.
