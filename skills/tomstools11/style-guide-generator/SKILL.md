---
name: style-guide-generator
description: Generate comprehensive website style guides and design systems from URLs, screenshots, and existing documentation. Use this skill when users ask to create a style guide, design system documentation, brand guidelines document, or design specification from a website, app, or existing materials. This skill produces professional PDF outputs following industry-standard style guide structure.
---

# Style Guide Generator

## Overview

Generate professionally formatted website style guides and design systems by analyzing provided URLs, screenshots, uploaded files, and user requirements. Output comprehensive PDF documents that serve as the single source of truth for design and development teams.

## Workflow Decision Tree

When a user requests a style guide, follow this decision tree:

1. **Gather Information**
   - If user provides URL → Use web_fetch to analyze the website
   - If user provides screenshots/images → Analyze visual elements
   - If user provides existing documentation → Extract and structure information
   - If user provides minimal information → Ask clarifying questions about brand, goals, and requirements

2. **Extract Design Elements**
   - Colors (primary, secondary, accent, text, background, success, warning, error)
   - Typography (fonts, weights, sizes, line heights)
   - Logo usage guidelines
   - Iconography style
   - Imagery preferences
   - UI component patterns
   - Layout and spacing systems
   - Accessibility requirements

3. **Structure Content**
   - Follow the standard template structure (see Template Structure section)
   - Organize extracted information into appropriate sections
   - Add mission/vision if provided or inferred
   - Document design principles
   - Create component specifications

4. **Generate PDF**
   - Use the PDF skill to create a professional document
   - Apply consistent formatting and typography
   - Include tables for color palettes, typography specs, and component states
   - Ensure accessibility with proper contrast ratios
   - Add version number and last updated date

## Standard Template Structure

Every style guide should follow this professional structure (based on industry best practices):

### 1.0 Introduction
- Version number and last updated date
- Purpose and scope statement
- Target audience (design and development teams)

### 1.1 Mission & Vision
- Company mission statement
- Company vision statement
- Strategic positioning

### 1.2 Design Principles
- 4-6 core principles that guide design decisions
- Each principle with name and description
- Examples: "Clarity Above All", "Empowerment Through Simplicity", "Consistency Builds Trust", "Human-Centered"

### 2.0 Brand Identity

#### 2.1 Logo Usage
- Primary logo specifications
- Clear space requirements
- Incorrect usage examples
- Minimum size requirements
- Color variations (full color, black, white)

#### 2.2 Color Palette
- Organized table with Role, Color Name, HEX, and RGB values
- Primary colors (1-2)
- Secondary colors (1-3)
- Accent colors
- Text colors
- Background colors
- System colors (Success, Warning, Error)
- Accessibility notes for each color combination

#### 2.3 Typography
- Heading font specifications (H1, H2, H3)
- Body text specifications
- Caption/small text specifications
- Font families, weights, sizes, and line heights in tabular format
- Web font loading considerations
- Fallback fonts

#### 2.4 Iconography
- Icon style guidelines (outlined, filled, line weight)
- Grid system specifications
- Size variants
- Usage examples
- Link to icon library

#### 2.5 Imagery
- Photography style guidelines
- Illustration style guidelines
- Image treatment specifications
- Do's and don'ts
- Quality requirements

### 3.0 Content Style Guide

#### 3.1 Voice and Tone
- Voice characteristics (consistent attributes)
- Tone variations (how voice adapts to context)
- Examples for different scenarios

#### 3.2 Grammar and Mechanics
- Punctuation rules
- Capitalization standards
- Voice preference (active/passive)
- Number formatting
- Date and time formatting

### 4.0 UI Components

#### 4.1 Buttons
- State variants (Primary, Secondary, Tertiary, Disabled)
- Size variants
- Usage guidelines
- Code snippets (HTML/CSS)
- Accessibility requirements

#### 4.2 Forms
- Input field specifications
- Label positioning
- Validation states
- Required field indicators
- Error message styling
- Help text formatting

#### 4.3 [Additional Components as needed]
- Cards
- Modals
- Navigation
- Tables
- Alerts/Notifications
- Tooltips
- Badges
- Progress indicators

### 5.0 Layout & Grid
- Grid system specifications (columns, gutters)
- Responsive breakpoints
- Spacing scale (base unit and multipliers)
- Container widths
- Margin and padding conventions

### 6.0 Accessibility (A11y)
- WCAG compliance level (2.1 AA standard)
- Color contrast requirements
- Alt text guidelines
- Keyboard navigation standards
- Screen reader considerations
- Focus indicators

### 7.0 Resources
- Links to design files (Figma, Sketch, Adobe XD)
- Icon library location
- Illustration library location
- Font files repository
- Code repository
- Additional documentation

### 8.0 Changelog
- Version history with dates
- Changes summary for each version

## Information Extraction Process

When analyzing provided materials, extract the following systematically:

### From URLs/Websites:
1. Fetch the website using web_fetch
2. Analyze HTML/CSS for:
   - Color values (background-color, color properties)
   - Font families and typography (font-family, font-size, font-weight)
   - Spacing patterns (margin, padding values)
   - Component structures
3. Take note of:
   - Visual hierarchy
   - Button styles and states
   - Form element treatments
   - Navigation patterns
   - Responsive behavior (if observable)

### From Screenshots/Images:
1. Identify color palette using visual analysis
2. Determine typography hierarchy
3. Note spacing and layout patterns
4. Identify UI component variants
5. Observe design principles in practice

### From Existing Documentation:
1. Extract mission/vision statements
2. Gather existing brand guidelines
3. Collect color specifications
4. Document current typography standards
5. Note any existing component libraries

## Creating Professional Tables

Use well-formatted tables for specifications. Example formats:

**Color Palette Table:**
```
| Role       | Color       | HEX     | RGB           |
|------------|-------------|---------|---------------|
| Primary    | Brand Blue  | #378DFF | 55, 141, 255  |
| Secondary  | Light Blue  | #A5CAFF | 165, 202, 255 |
```

**Typography Table:**
```
| Element | Font Family | Weight  | Size (px) | Line Height |
|---------|-------------|---------|-----------|-------------|
| H1      | Inter       | Bold    | 48        | 1.2         |
| H2      | Inter       | Bold    | 36        | 1.3         |
| Body    | Inter       | Regular | 16        | 1.5         |
```

**Button States Table:**
```
| State     | Appearance              | Usage                          |
|-----------|-------------------------|--------------------------------|
| Primary   | Solid fill, primary     | Main call to action on a page  |
| Secondary | Outline, primary color  | Secondary actions              |
| Tertiary  | Text only              | Less important actions         |
```

## PDF Generation Best Practices

1. **Professional Formatting:**
   - Use consistent heading hierarchy
   - Apply proper spacing between sections
   - Utilize tables for structured data
   - Include visual examples where possible

2. **Typography:**
   - Use professional fonts (Inter, Roboto, or system fonts)
   - Maintain consistent sizing hierarchy
   - Ensure sufficient line height for readability

3. **Color Usage:**
   - Show color swatches with hex codes
   - Ensure sufficient contrast for accessibility
   - Document color roles clearly

4. **Organization:**
   - Number sections clearly (1.0, 1.1, 2.0, etc.)
   - Include table of contents for longer guides
   - Use page breaks appropriately
   - Add page numbers

5. **Accessibility:**
   - Ensure document is screen-reader friendly
   - Use proper heading structure
   - Include alt text for images
   - Maintain minimum font size of 12pt

## Handling Incomplete Information

When information is missing or unclear:

1. **Make Reasonable Inferences:**
   - Extract colors from provided screenshots
   - Infer typography from website analysis
   - Estimate spacing based on visual patterns

2. **Use Placeholders:**
   - "[Insert company mission statement]" for unknown content
   - "[Link to design files]" for unavailable resources
   - "Version 1.0" and current date as defaults

3. **Ask Clarifying Questions:**
   - "What is your company's mission statement?"
   - "Do you have existing brand colors or should I extract them from the website?"
   - "Are there specific accessibility requirements beyond WCAG 2.1 AA?"

4. **Provide Templates:**
   - Include example text for sections that need user input
   - Show format for content they should provide
   - Give guidance on what information would be ideal

## Example User Interactions

**Example 1: URL-Based Request**
User: "Create a style guide for my website at example.com"
Process: 
1. Fetch website with web_fetch
2. Analyze HTML/CSS for design system
3. Extract colors, fonts, spacing
4. Structure into standard template
5. Generate professional PDF
6. Provide download link

**Example 2: Screenshot-Based Request**
User: "Here are screenshots of my app. Create a style guide." [uploads images]
Process:
1. Analyze images for visual elements
2. Extract color palette
3. Identify typography patterns
4. Document component styles
5. Fill in template structure
6. Generate PDF with findings
7. Provide download link

**Example 3: Comprehensive Request**
User: "Create a style guide using my website URL, these brand colors [list], and our mission statement [text]"
Process:
1. Combine all provided information
2. Fetch and analyze website
3. Integrate provided brand elements
4. Structure complete style guide
5. Generate professional PDF
6. Provide download link

## Quality Checklist

Before delivering the style guide PDF, verify:

- [ ] All sections are complete or marked as placeholders
- [ ] Color palette includes HEX and RGB values
- [ ] Typography specifications are detailed (family, weight, size, line height)
- [ ] Tables are properly formatted and aligned
- [ ] Accessibility requirements are documented
- [ ] Version number and date are included
- [ ] Resources section links are provided (even if placeholder)
- [ ] Changelog is started with version 1.0
- [ ] PDF is professionally formatted
- [ ] Document is ready for team distribution

## Resources

This skill uses the following bundled resources:

### assets/template.pdf
The base template PDF that demonstrates the professional structure and formatting that all generated style guides should follow. This file serves as a reference for structure, section organization, and formatting standards.

### scripts/analyze_website.py
Python script to extract design system information from websites, including colors, typography, and component patterns. Can be used to automatically gather design specifications from live URLs.

### references/design_system_examples.md
Reference document containing examples of well-structured design systems and style guides from leading companies. Use this for inspiration on content organization and presentation standards.
