"""Generate reference.html from _refdata.json (dumped from finvizfinance.constants)."""
import json, html, os

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, "_refdata.json")))

def esc(s):
    return html.escape(str(s))

def pills(items):
    return ('<div class="pill-list">'
            + "".join(f'<span class="pill">{esc(i)}</span>' for i in items)
            + "</div>")

SIDEBAR = """  <aside class="sidebar">
    <div class="brand">
      <a href="index.html">finvizfinance</a><br>
      <span class="ver">API Reference · v1.3.0</span>
    </div>
    <nav>
      <div class="nav-group">
        <div class="nav-title">Introduction</div>
        <a class="nav-link" href="index.html">Overview &amp; Setup</a>
      </div>
      <div class="nav-group">
        <div class="nav-title">Modules</div>
        <a class="nav-link" href="quote.html">Stock Quote</a>
        <a class="nav-link" href="screener.html">Screener</a>
        <a class="nav-link" href="group.html">Group</a>
        <a class="nav-link" href="market.html">Market Data</a>
        <a class="nav-link" href="charts.html">Forex · Crypto · Future</a>
        <a class="nav-link" href="utils.html">Configuration &amp; Utilities</a>
      </div>
      <div class="nav-group">
        <div class="nav-title">Appendix</div>
        <a class="nav-link active" href="reference.html">Reference Data</a>
        <a class="nav-sub" href="#signals">Signals</a>
        <a class="nav-sub" href="#orders">Orders (screener)</a>
        <a class="nav-sub" href="#groups">Group options</a>
        <a class="nav-sub" href="#group-orders">Orders (group)</a>
        <a class="nav-sub" href="#filters">Filters &amp; options</a>
        <a class="nav-sub" href="#custom-columns">Custom columns</a>
      </div>
    </nav>
  </aside>"""

parts = []
parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Reference Data — finvizfinance API</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="style.css">
<script>(function(){{try{{var t=localStorage.getItem('fvf-theme')||((window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches)?'dark':'light');document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}}})();</script>
<script src="docs.js" defer></script>
</head>
<body>
<div class="layout">
{SIDEBAR}
  <main class="content">
    <h1>Reference Data</h1>
    <p class="lead">The exact string values accepted by the screener and group APIs, extracted directly from
      <code>finvizfinance.constants</code> for v1.3.0. Use <kbd>Ctrl/Cmd-F</kbd> to search this page.</p>
    <div class="note">These lists are also available at runtime via the helper functions on the
      <a href="screener.html#helpers">Screener</a> and <a href="group.html#helpers">Group</a> pages.</div>
""")

# Signals
parts.append(f"""    <h2 id="signals">Trading signals <span class="badge">{len(data['signals'])}</span></h2>
    <p>Pass to <code>Screener.set_filter(signal=...)</code> or read from <code>Quote.ticker_signal()</code>.</p>
    {pills(data['signals'])}
""")

# Orders
parts.append(f"""    <h2 id="orders">Screener orders <span class="badge">{len(data['orders'])}</span></h2>
    <p>Pass to the <code>order</code> argument of a screener's <code>screener_view()</code> / <code>compare()</code>.</p>
    {pills(data['orders'])}
""")

# Groups
parts.append(f"""    <h2 id="groups">Group options <span class="badge">{len(data['groups'])}</span></h2>
    <p>Pass to the <code>group</code> argument of a group view's <code>screener_view()</code>.</p>
    {pills(data['groups'])}
""")

# Group orders
parts.append(f"""    <h2 id="group-orders">Group orders <span class="badge">{len(data['group_orders'])}</span></h2>
    <p>Pass to the <code>order</code> argument of a group view's <code>screener_view()</code>.</p>
    {pills(data['group_orders'])}
""")

# Filters & options
filters = data['filters']
parts.append(f"""    <h2 id="filters">Filters &amp; their options <span class="badge">{len(filters)} filters</span></h2>
    <p>Keys and values for the <code>filters_dict</code> passed to <code>Screener.set_filter()</code>. Each filter
      below lists its accepted option values. Click to expand.</p>
""")
for name, opts in filters.items():
    parts.append(f"""    <details>
      <summary>{esc(name)} <span class="badge">{len(opts)}</span></summary>
      <div class="details-body">{pills(opts)}</div>
    </details>
""")

# Custom columns
cols = data['custom_columns']
rows = "".join(
    f"<tr><td>{esc(k)}</td><td>{esc(v)}</td></tr>" for k, v in sorted(cols.items(), key=lambda kv: int(kv[0]))
)
parts.append(f"""    <h2 id="custom-columns">Custom screener columns <span class="badge">{len(cols)}</span></h2>
    <p>Index → column name, for the <code>columns</code> argument of <a href="screener.html#custom"><code>screener.Custom</code></a>.</p>
    <table class="params">
      <tr><th>Index</th><th>Column name</th></tr>
      {rows}
    </table>
""")

parts.append("""    <div class="footer">
      finvizfinance v1.3.0 · <a href="index.html">Home</a> · Generated from <code>finvizfinance.constants</code>
    </div>
  </main>
</div>
</body>
</html>
""")

out = os.path.join(HERE, "reference.html")
open(out, "w").write("".join(parts))
print("wrote", out)
