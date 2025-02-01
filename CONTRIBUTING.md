# Contributing to Simple Slurm

We welcome contributions! Before submitting changes, please follow these guidelines:

## Reporting Issues
- Check existing issues to avoid duplicates.
- Include a **minimal reproducible example** for bugs.
- If possible specify your Slurm cluster setup (*e.g.*, Slurm version, Linux distro).

## Submitting Pull Requests
1. **Fork the repository** and create a feature branch.
   ```bash
   git checkout -b my-feature
   ```
3. Ensure code passes:
   ```bash
   ruff check .            # Linting
   ruff format .           # Formatting
   python -m unittest -v   # Run unit tests
   ```
4. Test/validate changes (see [Testing](#testing)).
5. Update documentation if needed.
6. Open a Pull Request with a clear description of changes and test results.

## Code Style
- Format code with [`ruff`](https://docs.astral.sh/ruff/).
- Add type hints for new functions/methods.
- Keep docstrings consistent with existing code.

## Testing
- Add unit tests to validate any change in functionality.
- Testing on a real Slurm cluster is **highly desired**.
- A simple Slurm cluster is setup as an automatic action for any Pull Request.

## Questions?
- Open a GitHub issue.
- Tag [`@amq92`](https://github.com/amq92) in the discussion.

Thank you for helping improve Simple Slurm! 🚀
