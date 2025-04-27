# Security Policy

## Supported Versions

We provide security updates for each version until its End-of-Life (EOL) date. Below is a summary of currently supported versions:

| Version | Latest Release | End of Life | Notes                              |
| ------- | -------------- | ----------- | ---------------------------------- |
| 7.1     | 7.1.19         | TBD         | EOL to be determined               |
| 7.0     | 7.0.4          | 2025-03-11  | Reached EOL                        |
| 6.2     | 6.2.6          | 2025-08-22  | Supported for 1 year after 7.0.0   |
| 6.1     | 6.1.4          | 2025-01-12  | Reached EOL                        |
| 6.0     | 6.0.13         | 2024-09-23  | Reached EOL                        |
| 5.1     | 5.1.0          | 2024-08-31  | Reached EOL                        |
| 5.0     | 5.0.13         | 2024-08-31  | Reached EOL                        |
| < 5.0   | 4.4.12         | 2024-08-31  | Reached EOL                        |

## Version Support Guidelines

To ensure the security and stability of your PySNMP installation, please adhere to the following upgrade recommendations:

- **Always Upgrade to the Latest Patch Release**
  Patch releases address critical security vulnerabilities and bug fixes. Ensure you are using the latest patch version within your current major or minor release.
  *Example:* If you are on version 6.1.2, upgrade to 6.1.4.

- **Upgrade to the Next Minor Release Within 6 Months**
  Minor releases include new features and improvements. Upgrade to the latest minor version within 6 months after a new minor release is available to continue receiving security updates.
  *Example:* After 6.2.0 is released, upgrade to the latest 6.2.x within 6 months.

  > Note that our plan is to reduce this from 6 months to 3 months for 7.1.0 and above.

- **Upgrade to the Next Major Release Within 1 Year**
  Major releases may introduce significant changes and new functionalities. Upgrade to the latest major version within 1 year after a new major release to maintain support and security updates.
  *Example:* After 7.0.0 is released, upgrade to 7.x.x within 1 year.

### Recommended Upgrade Path

1. **Check Current Version**
   Verify your current PySNMP version to determine the necessary upgrades.

2. **Apply Latest Patch**
   Always apply the latest patch release for your current version to fix known vulnerabilities and bugs.

3. **Plan for Minor Upgrades**
   Schedule upgrades to the latest minor release within 6 months of its release to benefit from new features and continued security support.

4. **Schedule Major Upgrades**
   Plan to upgrade to the latest major release within 1 year of its release to ensure ongoing support and access to the latest advancements.

## Reporting a Vulnerability

If you discover a security vulnerability, please contact us directly at [LeXtudio Inc.](https://lextudio.com).
