# Resend SDK Installation Guide

## Detecting Project Language

Check for these files to determine the project's language/framework:

| File | Language | SDK |
|------|----------|-----|
| `package.json` | Node.js/TypeScript | resend |
| `requirements.txt` or `pyproject.toml` | Python | resend |
| `go.mod` | Go | resend-go/v3 |
| `Gemfile` | Ruby | resend |
| `composer.json` | PHP | resend/resend-php |
| `Cargo.toml` | Rust | resend-rs |
| `pom.xml` or `build.gradle` | Java | resend-java |
| `*.csproj` or `*.sln` | .NET | Resend |
| `mix.exs` | Elixir | resend |

## Installation Commands

### Node.js

```bash
npm install resend
```

Alternative package managers:
```bash
yarn add resend
pnpm add resend
bun add resend
```

### Python

```bash
pip install resend
```

### Go

```bash
go get github.com/resend/resend-go/v3
```

### Ruby

```bash
gem install resend
```

Or add to Gemfile:
```ruby
gem 'resend'
```

### PHP

```bash
composer require resend/resend-php
```

### Rust

```bash
cargo add resend-rs
cargo add tokio -F macros,rt-multi-thread
```

### Java

Gradle:
```gradle
implementation 'com.resend:resend-java:+'
```

Maven:
```xml
<dependency>
  <groupId>com.resend</groupId>
  <artifactId>resend-java</artifactId>
  <version>LATEST</version>
</dependency>
```

### .NET

```bash
dotnet add package Resend
```

### Elixir

Add to `mix.exs`:
```elixir
def deps do
  [
    {:resend, "~> 0.4.0"}
  ]
end
```

## API Key Setup

All SDKs require a Resend API key. Get one at https://resend.com/api-keys

Recommended: Store API key in environment variable `RESEND_API_KEY` rather than hardcoding.

## cURL (No SDK)

For quick tests or languages without an SDK, use the REST API directly:

```bash
curl -X POST 'https://api.resend.com/emails' \
  -H 'Authorization: Bearer re_xxxxxxxxx' \
  -H 'Content-Type: application/json' \
  -d '{
    "from": "Acme <onboarding@resend.dev>",
    "to": ["delivered@resend.dev"],
    "subject": "hello world",
    "html": "<p>it works!</p>"
  }'
```
