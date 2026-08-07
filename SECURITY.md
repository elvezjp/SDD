[English](./SECURITY.md) | [日本語](./SECURITY_ja.md)

# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

We recommend always using the latest version.

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub Issues.**

If you discover a security vulnerability, please contact us at the following email address:

- **Email**: info@elvez.co.jp
- **Recipient**: Elvez Inc. (株式会社エルブズ)

### Information to Include in Your Report

Please provide the following information:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact and severity
- Suggested fix or mitigation (if available)
- Contact information (optional)

## Response Schedule

- **Initial response**: Within 48 hours
- **Status update**: Within 7 days
- **Resolution**: Depending on severity
  - Critical: Within 14 days
  - High: Within 30 days
  - Medium: Within 60 days
  - Low: Next release cycle

## Security Considerations

This repository contains Markdown documents and sample files, as well as executable Python and TypeScript code in `spec-ai-writer/`. Please be aware of the following:

- **File contents**: Sample files are for illustrative purposes only and do not contain actual credentials, API keys, or personal information
- **Links**: External links in documents point to public resources, but please verify URLs before clicking
- **Scripts**: Scripts in `docs/tools/scripts.md` are examples only. Please review the content thoroughly before executing in your environment
- **Dependencies**: This repository uses Python and npm packages. Run `pip audit` and `npm audit` regularly to check for known vulnerabilities in dependencies
- **Intended usage of spec-ai-writer**: `spec-ai-writer` is a development-support tool intended to be run on localhost (the same machine). Its API has no authentication, so do not expose it to a network (see [spec-ai-writer/README.md](spec-ai-writer/README.md#セキュリティ))

## Security Best Practices

When using this repository, we recommend:

1. Always use the latest version
2. When forking and modifying, do not include actual credentials or personal information in files
3. When adding scripts, test them in a sandbox environment before use
4. Verify that external links point to the intended URL before clicking

## Contact

For security-related questions that are not vulnerability reports:

- **GitHub Issues**: [https://github.com/elvezjp/SDD/issues](https://github.com/elvezjp/SDD/issues) (please add the `security` label)
- **Email**: info@elvez.co.jp
