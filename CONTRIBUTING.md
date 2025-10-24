# Contributing to Sora Video Generator

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR-USERNAME/halloween.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes thoroughly
6. Commit your changes: `git commit -m "Description of your changes"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Development Setup

1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your OpenAI API key:
   ```bash
   cp .env.example .env
   ```
4. Edit `.env` and add your `OPENAI_API_KEY`

## Code Guidelines

### Python Style

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and single-purpose

### Testing

- Test your changes with actual API calls (be mindful of costs)
- Verify error handling works correctly
- Test edge cases (missing files, invalid inputs, etc.)

## Types of Contributions

### Bug Reports

When reporting bugs, please include:
- Python version
- Operating system
- Steps to reproduce the issue
- Expected vs actual behavior
- Error messages and stack traces

### Feature Requests

When suggesting features:
- Explain the use case
- Describe how it would work
- Consider backward compatibility
- Note any API limitations

### Code Contributions

We welcome:
- Bug fixes
- New features
- Documentation improvements
- Performance optimizations
- Better error handling
- Additional video generation options

### Documentation

- Fix typos and clarify instructions
- Add examples and use cases
- Improve setup instructions
- Document undocumented features

## Pull Request Process

1. **Update documentation**: If you add/change functionality, update README.md and CLAUDE.md
2. **Test thoroughly**: Ensure your changes work as expected
3. **Keep PRs focused**: One feature or fix per PR
4. **Write clear commit messages**: Explain what and why
5. **Respond to feedback**: Be open to suggestions and improvements

## Code Review

All submissions require review. We'll provide feedback and may request changes. This is a normal part of the process to ensure code quality.

## API Cost Considerations

Remember that Sora 2 API calls cost money (~$3 per 10-second video). When testing:
- Use the shortest duration possible (4 seconds)
- Delete test videos after verifying they work
- Consider the cost impact of features you add

## Questions?

If you have questions about contributing, feel free to:
- Open an issue for discussion
- Ask in pull request comments
- Check existing issues for similar questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
