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
    <title>Curriculum Vitæ</title>
    <style>
      body {
        font-family: Verdana, "Trebuchet MS", Tahoma, Helvetica, sans-serif;
        background-color: #FFF;
        color: #000;
      }
      main {
        max-width: 50em;
        margin: 0 auto;
      }
      @media print {
        main {
          max-width: 60em;
        }
      }

      h1, h2, h3 {
        line-height: 1em;
      }
      h1 {
        text-align: center;
        font-size: 2em;
        margin: 0.5em 0;
        page-break-after: avoid;
        page-break-before: avoid;
        line-height: 1em;
      }
      h2 {
        text-align: center;
        font-size: 1.25em;
        margin: 1.2em 0 0;
        color: #FFF;
        background: #000;
        padding: 0.2em 1em;
        page-break-after: avoid;
      }
      @media print {
        h2 {
          background: #FFF;
          border-top: 1px dotted #000;
          border-bottom: 1px dotted #000;
          color: #000;
        }
      }
      h3 {
        font-size: 1em;
        margin: 1.5em 0 0;
      }
      section.entry {
        page-break-inside: avoid;
      }

      .two-cols-header {
        margin: 1em 0 0;
        display: table;
        width: 100%;
        clear: both;
      }
      .two-cols-header > * {
        display: table-cell;
      }
      .two-cols-header > *:nth-child(2) {
        text-align: right;
      }

      .time {
        font-weight: bold;
        font-size: 0.8em;
        color: #333;
      }

      .logo {
        max-height: 3em;
        max-width: 10em;
        float: right;
        margin: 1em;
      }

      p {
        margin: 0.5em 0;
        text-align: justify;
      }
      small {
        font-size: 0.8em;
        color: #666;
      }
      .tech {
        font-size: 0.8em;
        color: #666;
      }

      .compact {
        display: table;
        margin: 0 2em;
        page-break-inside: avoid;
      }
      .compact > section {
        display: table-row;
      }
      .compact > section > * {
        display: table-cell;
        padding: 0.25em 1em;
      }

      a, a:link, a:visited {
        color: #009;
        text-decoration: none;
      }
      a:hover, a:active, a:focus {
        background-color: #FF9;
      }
      @media print {
        a, a:link, a:visited, a:hover, a:focus, a:active {
          color: #000;
          background-color: #FFF;
          text-decoration: none;
        }
      }
    </style>
    <main>
      <h1>Curriculum Vitæ</h1>
      <xsl:apply-templates />
    </main>
  </xsl:template>

  <xsl:template match="present"><span class="present">present</span></xsl:template>

  <xsl:template match="/cv/group">
    <section>
      <xsl:attribute name="class">group <xsl:value-of select="@style"/></xsl:attribute>
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
        <xsl:when test="time">
          <div class="two-cols-header">
            <xsl:apply-templates select="head" />
            <xsl:apply-templates select="time" />
          </div>
          <xsl:if test="@logo">
            <img alt="" class="logo">
              <xsl:attribute name="src">
                <xsl:value-of select="@logo" />
              </xsl:attribute>
            </img>
          </xsl:if>
        </xsl:when>
        <xsl:otherwise>
          <xsl:if test="@logo">
            <img alt="" class="logo">
              <xsl:attribute name="src">
                <xsl:value-of select="@logo" />
              </xsl:attribute>
            </img>
          </xsl:if>
          <xsl:apply-templates select="head" />
        </xsl:otherwise>
      </xsl:choose>
      <xsl:apply-templates select="p" />
      <xsl:apply-templates select="tech" />
    </section>
  </xsl:template>

  <xsl:template match="time">
    <div class="time">
      <xsl:apply-templates select="node()" />
    </div>
  </xsl:template>

  <xsl:template match="cv/group/entry/tech">
    <p class="tech">Technologies: <strong><xsl:apply-templates select="node()" /></strong></p>
  </xsl:template>

</xsl:stylesheet>
