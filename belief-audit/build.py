#!/usr/bin/env python3
"""Builds The Belief Audit workbook (HTML -> PDF via headless Chromium)."""
import subprocess, pathlib

OUT = pathlib.Path(__file__).parent
CSS = """
@page { size: 8.5in 11in; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: 'Liberation Sans', 'DejaVu Sans', sans-serif; color: #1a1126; font-size: 11pt; line-height: 1.42; }
.page { width: 8.5in; height: 11in; position: relative; overflow: hidden; page-break-after: always; background: #faf7ff; }
.page:last-child { page-break-after: auto; }
.serif { font-family: 'Bitstream Charter', 'DejaVu Serif', serif; }

/* header band */
.band { background: radial-gradient(ellipse at 85% -40%, #4c1d95 0%, #1b0b36 45%, #0b0712 100%); color: #fff; padding: 0.45in 0.75in 0.3in; height: 1.65in; position: relative; }
.band .kicker { font-size: 9pt; letter-spacing: 0.32em; text-transform: uppercase; color: #c4b5fd; }
.band h1 { font-family: 'Bitstream Charter', 'DejaVu Serif', serif; font-weight: normal; font-size: 27pt; line-height: 1.1; margin: 0.1in 0 0; color: #fff; max-width: 5.6in; }
.band .orb { position: absolute; right: 0.55in; top: 0.35in; }
.rule { height: 4px; background: linear-gradient(90deg, #7c3aed, #c4b5fd 55%, rgba(196,181,253,0)); }
.body { padding: 0.26in 0.75in 0.6in; }
.body p { margin: 0 0 0.11in; }
h3 { font-family: 'Bitstream Charter', 'DejaVu Serif', serif; font-weight: normal; font-size: 13.5pt; color: #4c1d95; margin: 0.16in 0 0.07in; }
.eyebrow { font-size: 8.5pt; letter-spacing: 0.22em; text-transform: uppercase; color: #7c3aed; margin: 0.16in 0 0.05in; font-weight: bold; }
.story { background: #efe7fd; border-left: 4px solid #7c3aed; padding: 0.11in 0.2in 0.04in; border-radius: 0 8px 8px 0; margin: 0.06in 0 0.12in; }
.story p { margin-bottom: 0.08in; }
.quote { font-family: 'Bitstream Charter', 'DejaVu Serif', serif; font-style: italic; color: #4c1d95; }
ol.steps { margin: 0.04in 0 0.1in; padding: 0; list-style: none; counter-reset: s; }
ol.steps li { counter-increment: s; position: relative; padding: 0.03in 0 0.03in 0.44in; }
ol.steps li::before { content: counter(s); position: absolute; left: 0; top: 0.03in; width: 0.28in; height: 0.28in; border-radius: 50%; background: #1b0b36; color: #ddd0ff; font-size: 9.5pt; text-align: center; line-height: 0.28in; font-weight: bold; }
ul.dots { margin: 0.02in 0 0.1in; padding: 0; list-style: none; }
ul.dots li { position: relative; padding: 0.025in 0 0.025in 0.24in; }
ul.dots li::before { content: ''; position: absolute; left: 0.04in; top: 0.13in; width: 0.09in; height: 0.09in; transform: rotate(45deg); background: #7c3aed; }
.lines { height: var(--h, 1.3in); background-image: repeating-linear-gradient(to bottom, transparent 0, transparent calc(0.3in - 1px), #cdbff0 calc(0.3in - 1px), #cdbff0 0.3in); margin: 0.05in 0 0.1in; }
.next { margin-top: 0.12in; padding: 0.1in 0.18in; border: 1px solid #cdbff0; border-radius: 8px; background: #fff; font-size: 10.5pt; color: #4c1d95; }
.next b { color: #1b0b36; letter-spacing: 0.1em; text-transform: uppercase; font-size: 8.5pt; }
.foot { position: absolute; left: 0.75in; right: 0.75in; bottom: 0.3in; font-size: 8pt; color: #8a77b3; display: flex; justify-content: space-between; letter-spacing: 0.08em; }
.note { font-size: 9.5pt; color: #5b4a82; }
.card table { border-collapse: separate; border-spacing: 0; width: 100%; border: 2px solid #4c1d95; border-radius: 10px; overflow: hidden; }
.card td { border-bottom: 1px solid #cdbff0; padding: 0.075in 0.14in; vertical-align: top; }
.card tr:last-child td { border-bottom: none; }
.card td.k { background: #1b0b36; color: #ddd0ff; width: 2.55in; font-size: 10pt; }
.card td.v { background: #fff; height: 0.36in; }
.darkbox { background: #0b0712; color: #efe9ff; border-radius: 12px; padding: 0.14in 0.3in 0.1in; margin-top: 0.18in; }
.darkbox h3 { color: #c4b5fd; margin-top: 0.1in; }
.darkbox ol.steps li::before { background: #3b1a7a; color: #fff; }
.darkbox .next { background: #160b2c; border-color: #3b2270; color: #c4b5fd; }
.darkbox .next b { color: #fff; }

/* cover */
.cover { background: radial-gradient(circle at 70% 28%, #5b21b6 0%, #2a1058 28%, #0b0712 66%); color: #fff; }
.cover .stars { position: absolute; inset: 0; }
.cover .title { position: absolute; left: 0.9in; right: 0.9in; top: 5.6in; }
.cover .title .kicker { font-size: 10pt; letter-spacing: 0.4em; text-transform: uppercase; color: #c4b5fd; }
.cover h1 { font-family: 'Bitstream Charter', 'DejaVu Serif', serif; font-weight: normal; font-size: 54pt; line-height: 1.04; margin: 0.18in 0 0.22in; }
.cover .sub { font-size: 14pt; color: #e4dbff; max-width: 5.6in; line-height: 1.45; }
.cover .by { position: absolute; left: 0.9in; bottom: 0.7in; font-size: 10pt; letter-spacing: 0.3em; text-transform: uppercase; color: #c4b5fd; }
.cover .free { position: absolute; right: 0.9in; bottom: 0.7in; font-size: 9pt; letter-spacing: 0.25em; text-transform: uppercase; color: #0b0712; background: #c4b5fd; padding: 0.06in 0.16in; border-radius: 20px; font-weight: bold; }

/* start page */
.dark { background: #0b0712; color: #efe9ff; }
.dark .body { padding-top: 0.5in; }
.dark h3 { color: #c4b5fd; }
.dark .eyebrow { color: #a78bfa; }
.dark ul.dots li::before { background: #a78bfa; }
.dark .foot { color: #7a69a8; }
.dark .next { background: #160b2c; border-color: #3b2270; color: #c4b5fd; }
.dark .next b { color: #fff; }
.help { background: #160b2c; border: 1px solid #3b2270; border-radius: 10px; padding: 0.12in 0.2in 0.05in; margin: 0.08in 0 0.1in; }
"""

ORB = """<svg class="orb" width="110" height="110" viewBox="0 0 110 110">
<defs><radialGradient id="g" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#c4b5fd" stop-opacity=".9"/><stop offset="1" stop-color="#7c3aed" stop-opacity="0"/></radialGradient></defs>
<circle cx="55" cy="55" r="52" fill="url(#g)" opacity=".35"/>
<circle cx="55" cy="55" r="38" fill="none" stroke="#c4b5fd" stroke-opacity=".5"/>
<circle cx="55" cy="55" r="26" fill="none" stroke="#c4b5fd" stroke-opacity=".7"/>
<path d="M62 31a24 24 0 1 0 0 48 19 19 0 1 1 0-48z" fill="#ede9fe"/>
</svg>"""

COVER_ART = """<svg class="stars" viewBox="0 0 816 1056" preserveAspectRatio="xMidYMid slice">
<defs><radialGradient id="halo" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ddd6fe" stop-opacity=".55"/><stop offset=".5" stop-color="#8b5cf6" stop-opacity=".18"/><stop offset="1" stop-color="#8b5cf6" stop-opacity="0"/></radialGradient></defs>
<g transform="translate(520 300)">
<circle r="250" fill="url(#halo)"/>
<circle r="215" fill="none" stroke="#c4b5fd" stroke-opacity=".22"/>
<circle r="165" fill="none" stroke="#c4b5fd" stroke-opacity=".32"/>
<circle r="115" fill="none" stroke="#c4b5fd" stroke-opacity=".45"/>
<path d="M30 -105 a105 105 0 1 0 0 210 82 82 0 1 1 0 -210z" fill="#f5f3ff"/>
</g>
<g fill="#ede9fe">
<circle cx="90" cy="110" r="2.2"/><circle cx="210" cy="60" r="1.6"/><circle cx="330" cy="150" r="2"/><circle cx="140" cy="260" r="1.4"/>
<circle cx="260" cy="340" r="2.4"/><circle cx="70" cy="420" r="1.6"/><circle cx="740" cy="90" r="2"/><circle cx="700" cy="560" r="1.8"/>
<circle cx="400" cy="480" r="1.4"/><circle cx="600" cy="40" r="1.6"/><circle cx="780" cy="330" r="1.6"/><circle cx="170" cy="520" r="1.4"/>
</g>
</svg>"""

def foot(n):
    return f'<div class="foot"><span>THE BELIEF AUDIT</span><span>{n}</span></div>'

def band(kicker, title):
    sz = ' style="font-size:23pt"' if len(title) > 26 else ''
    return f'<div class="band"><div class="kicker">{kicker}</div><h1{sz}>{title}</h1>{ORB}</div><div class="rule"></div>'

def page(n, kicker, title, inner):
    return f'<section class="page">{band(kicker, title)}<div class="body">{inner}</div>{foot(n)}</section>'

def steps(items):
    return '<ol class="steps">' + ''.join(f'<li>{i}</li>' for i in items) + '</ol>'

def lines(h):
    return f'<div class="lines" style="--h:{h}in"></div>'

def nxt(t):
    return f'<div class="next"><b>What\'s next</b>&nbsp;&nbsp; {t}</div>'


TRI = """<svg width="62%" viewBox="0 0 640 250" style="margin:0 19% 0.02in">
<defs><radialGradient id="c3" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#7c3aed" stop-opacity=".95"/><stop offset="1" stop-color="#4c1d95" stop-opacity=".95"/></radialGradient></defs>
<g stroke="#8b5cf6" stroke-opacity=".6" stroke-width="2">
<line x1="320" y1="125" x2="115" y2="70"/><line x1="320" y1="125" x2="525" y2="70"/><line x1="320" y1="125" x2="320" y2="215"/></g>
<circle cx="320" cy="125" r="46" fill="url(#c3)"/>
<text x="320" y="121" text-anchor="middle" fill="#fff" font-size="13" font-family="Liberation Sans">The</text>
<text x="320" y="139" text-anchor="middle" fill="#fff" font-size="13" font-family="Liberation Sans">belief</text>
<g font-family="Liberation Sans" text-anchor="middle">
<circle cx="115" cy="70" r="52" fill="#1b0b36"/><text x="115" y="66" fill="#ddd0ff" font-size="14" font-weight="bold">Repetition</text><text x="115" y="84" fill="#a78bfa" font-size="10.5">heard again</text>
<circle cx="525" cy="70" r="52" fill="#1b0b36"/><text x="525" y="66" fill="#ddd0ff" font-size="14" font-weight="bold">Identity</text><text x="525" y="84" fill="#a78bfa" font-size="10.5">who you are</text>
<circle cx="320" cy="205" r="40" fill="#1b0b36"/><text x="320" y="196" fill="#ddd0ff" font-size="11.5" font-weight="bold">Social</text><text x="320" y="211" fill="#ddd0ff" font-size="11.5" font-weight="bold">transmission</text><text x="320" y="228" fill="#a78bfa" font-size="9.5">said out loud</text></g>
</svg>"""

LAD = """<svg width="80%" viewBox="0 0 640 215" style="margin:0 10% 0.02in">
<g font-family="Liberation Sans">
<g><rect x="30" y="8" width="580" height="32" rx="8" fill="#1b0b36"/><text x="48" y="29" fill="#ddd0ff" font-size="12.5">1. Why do I believe this?</text></g>
<g><rect x="55" y="48" width="555" height="32" rx="8" fill="#2a1058"/><text x="73" y="69" fill="#ddd0ff" font-size="12.5">2. Why does that matter?</text></g>
<g><rect x="80" y="88" width="530" height="32" rx="8" fill="#3b1a7a"/><text x="98" y="109" fill="#efe9ff" font-size="12.5">3. Why did I take it as true?</text></g>
<g><rect x="105" y="128" width="505" height="32" rx="8" fill="#5b21b6"/><text x="123" y="149" fill="#fff" font-size="12.5">4. Why do I keep saying it?</text></g>
<g><rect x="130" y="168" width="480" height="32" rx="8" fill="#7c3aed"/><text x="148" y="189" fill="#fff" font-size="12.5" font-weight="bold">5. Why does that matter now? (stop at a feeling or a person)</text></g>
</g></svg>"""

pages = []

# ---- cover
pages.append(f"""<section class="page cover">{COVER_ART}
<div class="title"><div class="kicker">A Free Workbook</div><h1>The Belief<br>Audit</h1>
<div class="sub">Find where a limiting belief came from. See what kept it alive. Then take the first step to change it.</div></div>
<div class="by">~ Anna</div><div class="free">Free</div></section>""")

# ---- start here (dark)
pages.append(f"""<section class="page dark"><div class="band" style="background:transparent;height:1.5in"><div class="kicker">Welcome</div><h1>Start here</h1>{ORB}</div><div class="rule"></div>
<div class="body">
<p>If you've ever said "I'm just not a ___ person" or "I'm the one who...", this workbook is for you.</p>
<p>Some beliefs you chose. Some came from people, or from what happened to you, and were repeated until they sounded like facts about who you are. This workbook helps you find one of the second kind and take the first step to change it.</p>
<p>This isn't for people who want to repeat a nice phrase and hope. It's for people willing to ask where a belief came from and test it against their own life.</p>
<p>You will work on one belief. By the end you will have a Belief Card: the belief, where it came from, what kept it alive, the times it was not true, and affirmations to replace it.</p>
<h3>What you will have after each part</h3>
<ul class="dots">
<li><b>Part 1:</b> the smallest belief to work on.</li>
<li><b>Part 2:</b> a map of where it came from and what kept it alive.</li>
<li><b>Part 3:</b> a ladder of five whys.</li>
<li><b>Part 4:</b> the times the belief was not true.</li>
<li><b>Part 5:</b> three affirmations to replace it, and one physical action.</li>
<li><b>Part 6:</b> your Belief Card, and how to add your next belief.</li>
</ul>
<h3>How to use it</h3>
<p>Go in order. Write your answers on paper or in the Notebook. Plan on about 20 minutes a part, and stop whenever you need to.</p>
<div class="help"><div class="eyebrow" style="margin-top:0">What this is not</div>
<p>This is a self-reflection workbook. It is not therapy, medical advice, or a diagnosis. If something heavy comes up, stop and reach out for real support:</p>
<ul class="dots"><li>Suicidal thoughts or self-harm: 988 Suicide &amp; Crisis Lifeline, call or text 988</li>
<li>Domestic violence or abuse: National Domestic Violence Hotline, 1-800-799-7233</li></ul></div>
<h3>Where to start</h3><p>Go to Part 1. Start with the smallest belief you can find.</p>
</div>{foot(2)}</section>""")

# ---- part 1
S1 = steps(['Write down the sentences you tell yourself about what you can\'t do, aren\'t, or never will. Start them with "I\'m the one who...", "I\'m not a ___ person", or "I\'m just..." Keep this on one page. You will add to it in each part.',
'Pick the smallest one, the belief that feels easiest to change. A small win gives you the momentum for the bigger ones.',
'Write it as one sentence, in the words you actually hear. Rate how true it feels, from 0 to 10. You will rate it again at the end.'])
pages.append(page(3, 'Part 1', 'Name the Belief', f"""
<p>A belief that was handed to you rarely arrives as an argument. It arrives as a sentence, repeated until it sounds like a fact about you. You can't change a belief you haven't put into words, so we start by naming one.</p>
<div class="eyebrow">How it looked for me</div>
<div class="story"><p>Someone in my family said everything twice. Then they added the same three words at the end: before you forget.</p>
<p class="quote">Take your coat before you forget. Take your coat before you forget.</p>
<p>I heard it for years. Somewhere in those years I started to forget things: a coat, a name, a plan. I told people I had a bad memory, and I said it like a fact I had always known about myself.</p>
<p>The belief was not "I forget sometimes." It was "I'm the one who forgets." It cost me my memory, and it cost me the ability to believe I could remember. I never tried to fix it, because I was the one who forgot. I first doubted the story around 30, six years ago, when I started asking how I could see what my beliefs were and change them. That was a big belief. Start smaller than I did.</p></div>
<div class="eyebrow">Do this now</div>
{S1}
{lines(1.6)}
{nxt('In Part 2, you will trace where this belief came from.')}"""))

# ---- part 2
TRI2 = TRI
S2 = steps(['Where did I first hear this, or first learn it? Name the person, the place, or the moment before you name the claim.',
'What happened that made it feel true? An event, a circumstance, or a pattern that kept repeating.',
'Did anyone ever give me an argument for it? Write yes or no. Then circle the force that kept it alive: heard again and again, "I\'m the one who...", or said to other people.'])
pages.append(page(4, 'Part 2', 'Trace the Source', f"""
<p>A belief has a first time you heard it or learned it. Finding that moment takes away some of its power, because a belief that came from a person or a circumstance is no longer a fact about you.</p>
<p>Three forces keep a belief alive: repetition, identity, and social transmission. Most beliefs that were handed to you used at least one.</p>
{TRI2}
<ul class="dots"><li><b>Repetition:</b> you heard it again and again. Familiarity starts to feel like truth.</li>
<li><b>Identity:</b> it became part of who you are. A message that says who we are is a membership card, not an argument.</li>
<li><b>Social transmission:</b> you repeated it to other people. What you say out loud hardens.</li></ul>
<div class="eyebrow">How it looked for me</div>
<div class="story"><p>Where did I first hear it? From someone in my family, said twice. Nobody gave me an argument. All three forces were at work. Repetition: I heard it for years. Identity: it became an essential part of my identity. Social transmission: I told people I had a bad memory, like it was a fact I had always known about myself.</p></div>
<div class="eyebrow">Do this now</div>
{S2}
{lines(0.25)}
{nxt('In Part 3, you will ask why, five times.')}"""))

# ---- part 3
S3 = steps(['Ask: why do I believe this? Write the answer. Then ask why again about your answer, until you have asked five times.',
'Stop when you reach a feeling or a person, not a fact. Write one sentence on what you notice.'])
pages.append(page(5, 'Part 3', 'Ask Why Five Times', f"""
<p>Awareness is the first move. When you can see a belief, you are no longer inside it, and that gap is where change starts. One simple way to widen it is to ask why, again and again, until you reach what is underneath.</p>
{LAD}
<div class="eyebrow">How it looks (an illustration, not a real person)</div>
<div class="story"><p><b>Belief: "I'm not a math person."</b></p>
<ol style="margin:0 0 0.08in 0.2in;padding:0">
<li>Why do I believe that? Because I failed a fractions quiz in fourth grade.</li>
<li>Why did one quiz matter so much? Because my teacher said some people just aren't math people.</li>
<li>Why did I take the teacher's word for it? Because she was the adult and I was nine.</li>
<li>Why did I keep saying it years later? Because my friends nodded, and it made me feel like I belonged.</li>
<li>Why does that matter now? Because I have been protecting a story about who I am, not looking at what I can do.</li></ol></div>
<div class="eyebrow">Do this now</div>
{S3}
{lines(0.9)}
{nxt('In Part 4, you will look for the times the belief was not true.')}"""))

# ---- part 4
S4 = steps(['List every time the belief was not true, even once. Include times you did the opposite, and times someone saw you differently. Keep it to facts: what happened, not what it meant.',
'Look at the list. Write one sentence: "The belief is not always true. Here is what I see."'])
pages.append(page(6, 'Part 4', 'The Times It Was Not True', f"""
<p>A belief that was handed to you was never tested. Nobody checked it against your life. So you check it now, and not by arguing with it. You look for the times it was wrong.</p>
<div class="eyebrow">How it looks (an illustration, not a real person)</div>
<div class="story"><p><b>Belief: "I'm not a math person."</b></p>
<ul class="dots"><li>I split a restaurant bill in my head last month and got it right.</li>
<li>I doubled a recipe without a calculator.</li>
<li>A coworker once asked me to check her budget numbers.</li></ul>
<p>None of these proves she is a math person. They prove the belief is not always true, and a belief with exceptions is no longer a fact.</p></div>
<div class="eyebrow">Do this now</div>
{S4}
{lines(2.4)}
{nxt('In Part 5, you will write affirmations to replace it, and do one physical thing.')}"""))

# ---- part 5
S5 = steps(['Write the opposite of your belief, then turn it into three affirmations. Start with one you already believe at least 8 out of 10. Make the second a step further, around 6. Make the third the one you are aiming for, even if you only believe it 4 or 5 out of 10. Each one must be true about something real. If you can\'t believe it at all, make it smaller.',
'Say your first affirmation out loud, once. Then pick one physical action that proves it, small enough to do right now, in the next five to ten minutes. Do it, and write down what you did.',
'Rate the belief again, from 0 to 10.'])
pages.append(page(7, 'Part 5', 'Replace It, Then Do One Physical Thing', f"""
<p>The same forces that built the belief can build a better one. Repetition, identity, and social transmission are not the problem. The line is whether the message tells the truth about something real. A replacement that is too big to believe will not hold, so write three affirmations, from the easiest to believe to the one you are aiming for.</p>
<p>Then do something physical. You have to do something in the real world to change a belief and your identity. For me, it was paying for ghostwriting training. I learned quickly that my writing can make money, and the old belief stopped being the only story I had.</p>
<div class="eyebrow">How it looks (an illustration, not a real person)</div>
<div class="story"><p><b>Old belief:</b> "I'm not a math person."</p>
<p><b>Affirmation 1 (easy to believe):</b> "I got some math right this week."</p>
<p><b>Affirmation 2:</b> "I can learn the math I don't know yet."</p>
<p><b>Affirmation 3 (the one you are aiming for):</b> "I'm someone who can work with numbers."</p>
<p><b>Physical action:</b> add up one receipt and check the total.</p></div>
<div class="eyebrow">Do this now</div>
{S5}
{lines(1.6)}
{nxt('In Part 6, you will put it all on one card.')}"""))

# ---- part 6
rows = ['The belief','Where it came from (Part 2)','The force that kept it alive (Part 2)','What I found at the bottom of the whys (Part 3)','Times it was not true (Part 4)','My affirmations (Part 5)','My physical action, done (Part 5)','How true it felt at the start (0 to 10)','How true it feels now (0 to 10)']
card = '<div class="card"><table>' + ''.join(f'<tr><td class="k">{r}</td><td class="v"></td></tr>' for r in rows) + '</table></div>'
pages.append(page(8, 'Part 6', 'Your Belief Card and Next Steps', f"""
{card}
<div class="darkbox">
<div class="eyebrow" style="color:#a78bfa;margin-top:0">Then add beliefs slowly</div>
<p style="margin-bottom:0.04in">One belief at a time. Go back to your list from Part 1.</p>
<ol class="steps"><li>Pick the next smallest belief, the one that feels easiest to change.</li><li>Run it through Parts 2 to 5 again. It goes faster the second time.</li><li>Each small win gives you the momentum to take on a larger belief.</li><li>Save the biggest belief for last.</li></ol>
<div class="next"><b>What's next</b>&nbsp;&nbsp; This is one belief. You probably have more.</div>
</div>"""))

html = f'<!doctype html><html><head><meta charset="utf-8"><title>The Belief Audit</title><style>{CSS}</style></head><body>' + ''.join(pages) + '</body></html>'
(OUT / 'belief-audit.html').write_text(html, encoding='utf-8')

chrome = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
subprocess.run([chrome, '--headless=new', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer',
                f'--print-to-pdf={OUT / "The-Belief-Audit.pdf"}', f'file://{OUT / "belief-audit.html"}'], check=True, timeout=120)
print('done')
