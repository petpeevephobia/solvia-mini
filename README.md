# Solvia Labs Website

A modern, responsive website for Solvia Labs startup with Jekyll-powered case study pages.

## Features

- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Modern UI**: Clean, professional design with smooth animations
- **Fast Loading**: Optimized for performance with compressed assets
- **SEO Ready**: Semantic HTML structure and meta tags
- **Contact Form**: Functional contact form with validation
- **Smooth Scrolling**: Enhanced navigation experience
- **Jekyll CMS**: Dynamic case study pages with markdown content management

## Running Locally for Development

### Quick Start (Easiest Method)

The simplest way to run this website locally is using Python's built-in HTTP server:

1. **Open Terminal/Command Prompt** in the project root directory
2. **Run the server**:
   ```bash
   # Python 3 (most common)
   python -m http.server 8000
   
   # Or if you have Python 2
   python -m SimpleHTTPServer 8000
   ```
3. **Open your browser** and visit: `http://localhost:8000`

The site will automatically reload when you make changes to HTML/CSS/JS files (just refresh your browser).

#### Using Jekyll (Do this before pushing to Git)
If you need to work with case study pages that use Jekyll:

1. **Install Jekyll** (see Jekyll Setup section below)
2. **Run Jekyll server**:
   ```bash
   bundle exec jekyll serve
   ```
3. **View site**: Open `http://localhost:4000`

> **Note**: For most development work (editing HTML, CSS, JavaScript), the simple Python server method is sufficient. Only use Jekyll if you're working on case study pages.

### Troubleshooting

- **Port already in use?** Change the port number (e.g., `8000` to `8001`)
- **Can't find Python?** Make sure Python is installed and added to your PATH
- **Files not updating?** Hard refresh your browser (Ctrl+F5 or Cmd+Shift+R)

## File Structure

```
solvialabs-website/
├── index.html          # Main HTML file
├── product.html        # Product page
├── 404.html           # Custom 404 error page
├── _config.yml        # Jekyll configuration
├── _layouts/          # Jekyll layouts
│   └── case-study.html # Case study template
├── _case-studies/     # Case study markdown files
│   ├── akar-co.md     # AKAR CO. case study
│   └── verd-movement.md # Verd Movement case study
├── css/
│   └── style.css      # Main stylesheet
├── js/
│   └── script.js      # JavaScript functionality
├── assets/
│   ├── images/        # Image assets
│   └── README.md      # Assets documentation
└── README.md          # This file
```

## Jekyll Setup & Development

### Prerequisites
- Ruby 2.7 or higher
- Jekyll 4.0 or higher
- Bundler gem

### Installation
1. **Install Jekyll**: `gem install jekyll bundler`
2. **Install Dependencies**: `bundle install`
3. **Build Site**: `bundle exec jekyll build`
4. **Serve Locally**: `bundle exec jekyll serve`
5. **View Site**: Open `http://localhost:4000` in your browser

### Adding New Case Studies
1. Create a new markdown file in `_case-studies/` directory
2. Use the following front matter structure:

```yaml
---
layout: case-study
title: "Your Project Title"
client: "Client Name"
description: "Brief project description"
hero_image: "/assets/images/your-hero-image.jpg"
live_url: "https://your-live-site.com"
tags:
  - "Web Design"
  - "Brand Identity"

# Project Details
role: "Your Role"
timeline: "Project Duration"
year: "2024"

# Overview Section
overview:
  background: "Background information about the project"
  goals:
    - "Goal 1"
    - "Goal 2"
  target_users: "Description of target users"

# Continue with other sections...
---
```

3. The case study will automatically be available at `/case-studies/your-filename/`

## Deployment to Hostinger

1. **Build Jekyll Site**: `bundle exec jekyll build`
2. **Upload Files**: Upload the `_site` folder contents to your domain's public_html folder
3. **Configure Domain**: Point your domain to the hosting account
4. **SSL Certificate**: Enable SSL certificate in Hostinger control panel
5. **Test**: Visit your domain to ensure everything works

## Customisation

### Colours
The main brand colour is defined in CSS variables. Update the gradient colours in `css/style.css`:
- Primary: `#667eea` to `#764ba2`
- You can change these throughout the file

### Content
- Update company information in `index.html`
- Replace placeholder images in `assets/images/`
- Modify contact information and social links

### Images Needed
- Hero image (1200x800px recommended)
- Company logo
- Service icons
- Favicon (32x32px)

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers

## Performance

- Optimized CSS and JavaScript
- Compressed images recommended
- Gzip compression enabled via .htaccess
- Browser caching configured

## Contact

## Case Study Template Structure

The case study template includes the following sections:

1. **Hero Section**: Project tags, title, client, description, and hero image
2. **Project Details Bar**: Client, role, timeline, and year
3. **Overview Section**: Background, project goals, and target users
4. **The Challenge Section**: 5 key problems and user research statistics
5. **Design Process Section**: User research details, process image, and 4 key design decisions
6. **The Solution Section**: 3 core principles, 2 showcase images, and 4 key features
7. **Impact & Results Section**: 3 success metrics and qualitative feedback
8. **Key Takeaways Section**: 4 design lessons learned

## Contact

For questions about this website template, contact nadra@solvia.app.
