<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" encoding="utf-8" indent="yes" />

  <xsl:template match="@*|node()" priority="-1.0">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>


  <xsl:template match="/cv">
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <base href="https://mina86.com/" />
    <title>Michał Nazarewicz — Curriculum Vitæ</title>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&amp;family=Libre+Baskerville:wght@400;700&amp;family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&amp;display=swap');

      * {
        box-sizing: content-box;
        margin: 0;
        padding: 0
      }

      body, main {
        font-family: Lato, DejaVu Sans, Noto Sans, Verdana, sans-serif;
        background: #FFF;
        color: #000;
        line-height: 1.5;
      }

      h1, h2, h3 {
        font-family: Libre Baskerville, Georgia, Charter, Utopia, serif;
        font-weight: bold;
        page-break-after: avoid;
      }
      h1, h2 {
        text-align: center;
      }
      h1 {
        font-size: 2em;
        margin: 0.25em 0 0;
        page-break-before: avoid;
      }
      h2 {
        font-size: 1.25em;
        padding: 0.125em 0;
        margin: 1rem 0;
      }
      h3 {
        margin: 1em 0;
        font-size: 1em;
        font-weight: normal;
      }
      .entry {
        margin-bottom: 1.5em;
        page-break-inside: avoid;
      }

      .contact {
        page-break-inside: avoid;
        page-break-before: avoid;
      }
      .contact ul {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: center;
        gap: 1em;
      }
      .contact li {
        display: block;
      }

      .icon {
        font-family: Material Symbols Rounded;
        font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 20;
        color: #657b83;
        margin-right: 0.25em;
        position: relative;
        top: 0.125em;
      }

      p, .entry ul {
        margin: 0.5em 0;
        text-align: justify;
      }
      .entry ul {
        padding-left: 1.5em;
      }
      .time {
        margin: -1em 0 0;
        font-weight: bold;
        font-size: 0.75em;
        color: #586e75;
      }
      .logo, svg {
        width: auto;
        height: auto;
        max-width:  8em; max-width:  min(20vw, 8em);
        max-height: 3em; max-height: min(54vw, 3em);
        float: right;
        margin: 0 0 0.5em 1em;
      }
      @media (max-width: 20em) {
        .logo, svg { display: none }
      }
      .tech {
        color: #586e75;
      }


      a, a:link, a:visited, a:hover, a:focus, a:active {
        color: inherit;
        background: transparent;
        text-decoration: none;
      }

      @media screen {
        body { background: #93a1a1; }
        @media (prefers-color-scheme: dark) {
          body { background: #073642; }
        }
        main {
          background: #fdf6e3;
          color: #073642;
          max-width: 44em;
          margin: 0 auto;
          padding: 1em;
          padding: 1em clamp(1em, calc(25vw - 11em), 5em);
          box-shadow: 0 0 1em #000;
        }

        h1, h2 {
          color: #0fa74a;
        }
        h1 {
          margin: 0;
          page-break-before: avoid;
        }
        h2 {
          border-bottom: 1px dashed #0fa74a;
        }

        a, a:link, a:visited {
          color: #268bd2;
        }
        a:hover, a:active, a:focus {
          text-decoration: underline;
        }
      }

      @media print {
        body {
          line-height: 1.25;
        }
      }
    </style>
    <main>
      <h1>Michał Nazarewicz</h1>
      <xsl:apply-templates />
    </main>
  </xsl:template>

  <xsl:template match="/cv/contact">
    <section class="contact">
      <ul>
        <xsl:apply-templates select="li" />
      </ul>
    </section>
  </xsl:template>

  <xsl:template match="/cv/group">
    <section>
      <xsl:apply-templates select="head" />
      <xsl:apply-templates select="entry" />
    </section>
  </xsl:template>

  <xsl:template match="group/head">
    <h2><xsl:apply-templates select="node()" /></h2>
  </xsl:template>

  <xsl:template match="group/entry/head">
    <h3><xsl:apply-templates select="node()" /></h3>
  </xsl:template>

  <xsl:template match="entry">
    <section class="entry">
      <xsl:choose>
        <xsl:when test="contains(@logo, '.svg')">
          <xsl:copy-of select="document(@logo)" />
        </xsl:when>
        <xsl:when test="@logo">
          <img alt="" class="logo">
            <xsl:attribute name="src">
              <xsl:value-of select="@logo" />
            </xsl:attribute>
          </img>
        </xsl:when>
      </xsl:choose>

      <xsl:apply-templates select="head" />
      <xsl:if test="position | company">
        <h3>
          <xsl:if test="position">
            <xsl:apply-templates select="position" /> at
          </xsl:if>
          <xsl:apply-templates select="company" />
        </h3>
      </xsl:if>
      <xsl:apply-templates select="time" />
      <xsl:apply-templates select="p | ul" />
      <xsl:apply-templates select="tech" />
    </section>
  </xsl:template>

  <xsl:template match="position | company">
    <b><xsl:apply-templates select="node()" /></b>
  </xsl:template>

  <xsl:template match="time">
    <div class="time">
      <xsl:apply-templates select="node()" />
    </div>
  </xsl:template>

  <xsl:template match="cv/group/entry/tech">
    <p class="tech">Technologies: <strong><xsl:apply-templates select="node()" /></strong></p>
  </xsl:template>

  <xsl:template match="li">
    <li>
      <xsl:if test="@icon">
        <span class="icon"><xsl:value-of select="@icon" /></span>
      </xsl:if>
      <xsl:apply-templates select="node()" />
    </li>
  </xsl:template>
</xsl:stylesheet>
