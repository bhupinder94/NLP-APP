from nlp_app.nlp.summarizer import summarize_long_text

text = """Artificial General Intelligence has become one of the most frequently repeated phrases in modern AI discourse, particularly when spoken by OpenAI’s leadership. For Sam Altman, AGI is not just a technical milestone but a defining goal, one he regularly references when discussing timelines, safety and the future of humanity. Now, that framing appears to have drawn a public rebuttal from Microsoft’s AI chief.

Mustafa Suleyman, the former Google DeepMind co-founder who now leads Microsoft’s AI division, has spoken openly against the idea of AGI as a race that can be won. Speaking on a recent podcast, Suleyman dismissed the popular narrative that treats AGI like a finish line where one company arrives first and claims victory.

According to Suleyman, the concept of an AGI race is fundamentally flawed. He said the language of racing implies a zero-sum outcome, where one winner stands above everyone else. In his view, that analogy does not match how scientific progress or technological capability actually spreads. Knowledge, tools and breakthroughs tend to diffuse rapidly, often across borders and organisations, sometimes within months.He explained that talking about medals for first, second and third place suggests a moment where the competition ends. That assumption, he argued, is misleading. There is no single point at which intelligence becomes complete, and there is no fixed benchmark that permanently separates leaders from followers. Instead, progress happens across many dimensions and at multiple scales, often in parallel.

Suleyman’s comments stand in quiet contrast to the way AGI is often discussed by OpenAI. Under Altman, OpenAI has repeatedly framed AGI as a transformational threshold, one that carries enormous responsibility and risk. While Altman has emphasised safety and governance, he has also leaned into the idea that reaching AGI first matters, both strategically and historically.

Suleyman does not deny the importance of advanced AI or the need to move quickly. He acknowledged that every major lab is pushing as hard as possible. What he rejects is the notion that speed alone defines success. For him, the real objective is not supremacy over rivals but resilience and capability within an institution.

At Microsoft, Suleyman says his mandate is to build long-term self-sufficiency. That means ensuring the company can train large models from scratch, develop its own frontier systems and assemble world-class teams without relying entirely on external partners. The focus, he suggested, is on depth rather than headlines.This emphasis is notable given Microsoft’s close relationship with OpenAI. While the two companies remain deeply linked, Suleyman’s remarks signal that Microsoft is thinking beyond any single partnership or milestone. The goal is not to claim the title of first to AGI, but to ensure the company remains capable and competitive no matter how the field evolves.His position also reflects a broader shift in the AI industry. As models grow more powerful, the conversation is slowly moving away from dramatic end points and toward questions of sustainability, governance and integration into real-world systems. In that context, framing AGI as a trophy to be won may be more distracting than useful.
"""

summary = summarize_long_text(text)
print(summary)
