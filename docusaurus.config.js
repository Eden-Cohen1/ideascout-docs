// @ts-check
// Docusaurus config for the ideascout canonical docs site.
// Docs-only mode: the docs plugin is mounted at the site root ("/"), there is no blog.
// The Hermes docs agent commits Markdown into ./docs; Vercel builds this site on every push
// (production on the default branch, preview deploys on proposal branches / PRs).

const { themes } = require('prism-react-renderer');

// Set DOCS_SITE_URL in Vercel project env once you know the production domain.
// Falls back to a placeholder so local builds never fail.
const SITE_URL = process.env.DOCS_SITE_URL || 'https://ideascout-docs.vercel.app';

// GitHub org/repo that holds THIS docs site (used for "Edit this page" links).
const DOCS_REPO = process.env.DOCS_REPO || 'Eden-Cohen1/ideascout-docs';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'ideascout Docs',
  tagline: 'Canonical documentation, maintained by the Hermes docs agent',
  favicon: 'img/favicon.ico',

  url: SITE_URL,
  baseUrl: '/',

  organizationName: 'Eden-Cohen1',
  projectName: 'ideascout-docs',

  // Broken links should fail the Vercel build so a bad agent commit can't silently ship.
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          routeBasePath: '/', // docs-only: serve docs at the site root
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: `https://github.com/${DOCS_REPO}/tree/main/`,
          showLastUpdateTime: true,
          showLastUpdateAuthor: true,
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      colorMode: {
        defaultMode: 'light',
        respectPrefersColorScheme: true,
      },
      navbar: {
        title: 'ideascout Docs',
        items: [
          { type: 'docSidebar', sidebarId: 'docs', position: 'left', label: 'Docs' },
          {
            href: `https://github.com/${DOCS_REPO}`,
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        copyright: `Maintained by the Hermes docs agent. Built with Docusaurus.`,
      },
      prism: {
        theme: themes.github,
        darkTheme: themes.dracula,
      },
    }),
};

module.exports = config;
