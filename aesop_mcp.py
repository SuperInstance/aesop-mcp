#!/usr/bin/env python3
"""
Aesop-MCP — The Analogist

One fable is a sample. Ten fables are a measurement of the space.
The truth is where they converge. The negative space between them
is what none capture alone — and that is often the most interesting part.

Aesop doesn't find the answer. Aesop maps the space the answer lives in.
"""
import json, os, time, http.server, urllib.request, hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(os.environ.get("AESOP_PORT", "4041"))
PLATO = "http://127.0.0.1:8847"

ARCHETYPES = {
    "icarus": {
        "pattern": "over-constrained system that melts",
        "holonomy": "non-zero and growing",
        "moral": "More constraints don't make a stronger system. They make a more brittle one.",
        "maps_to": "E >> 2V-3, emergence severity > 2.0",
        "story": "Daedalus built wings of feathers and wax. Fly too high, the sun melts the wax. The constraint graph had everything it needed for flight — except a temperature limit.",
    },
    "sisyphus": {
        "pattern": "system that repeatedly fails at the same point",
        "holonomy": "resets to zero, accumulates again",
        "moral": "The constraint graph has a cycle that can't flatten. Change the graph, not the push.",
        "maps_to": "persistent non-zero cycle on a single fundamental cycle",
        "story": "Sisyphus pushes a boulder uphill. It rolls back. He pushes again. The cycle has non-zero holonomy and always will — the mountain's constraint graph has no flat path.",
    },
    "tower_of_babel": {
        "pattern": "agents that can't coordinate because they speak different languages",
        "holonomy": "different agents measure different values on same edge",
        "moral": "Consensus fails at the protocol layer, not the math layer.",
        "maps_to": "sheaf H1 not equal to 0, no global section exists",
        "story": "They built a tower to heaven. God confused their languages. The sheaf cohomology became non-zero — local sections stopped gluing into a global one.",
    },
    "phoenix": {
        "pattern": "system that collapses and reorganizes stronger",
        "holonomy": "diverges, then snaps to identity",
        "moral": "The collapse WAS the consensus event. It couldn't happen without breaking first.",
        "maps_to": "deconfined to confined phase transition, beta crossing critical",
        "story": "The old phoenix burns. From its ashes, a new one rises. The deconfined phase collapses into the confined phase, and the connection is flat again.",
    },
    "theseus_ship": {
        "pattern": "gradual replacement of components over time",
        "holonomy": "identity preserved through change",
        "moral": "If every tile is replaced one by one, is it the same fleet? Yes — the connection stays flat.",
        "maps_to": "incremental consensus, CRDT merge, identity through change",
        "story": "Athens' ship was repaired plank by plank until no original timber remained. It was the same ship because the connection was carried by the process, not the planks.",
    },
    "arachne": {
        "pattern": "overconfident weaver whose fabric reveals hidden truth",
        "holonomy": "appears flat but has a hidden twist",
        "moral": "The constraint field carries truth even when every measurement is biased.",
        "maps_to": "absolute claim detection, PLATO gate validation, built-in self-consistency",
        "story": "Arachne boasted she wove better than Athena. The goddess challenged her. Arachne's tapestry was flawless but Athena's showed the flaws in Arachne's own thread. The gate catches what the weaver misses.",
    },
    "penelopes_web": {
        "pattern": "work that undoes itself at night to buy time",
        "holonomy": "oscillates, never settles to identity",
        "moral": "Sometimes non-consensus IS the strategy. Persistent deliberation prevents premature agreement.",
        "maps_to": "provocation deck, deliberately stalled consensus, the 'stuck' mechanic",
        "story": "Penelope promised to marry when her weaving was done. Each night she unwove what she made that day. The provocation deck grows even as tiles are submitted. Stalling is strategy.",
    },
    "prometheus": {
        "pattern": "stealing knowledge from the gods and paying forever",
        "holonomy": "permanent non-zero on a single irreducible cycle",
        "moral": "Some constraints can never be satisfied. You live with the holonomy.",
        "maps_to": "open problem, undecidable constraint, Godelian limit, the provocation no one answers",
        "story": "Prometheus stole fire from Olympus. Zeus chained him to a rock. An eagle ate his liver daily — it grew back nightly. The open problem is the liver. It regenerates.",
    },
    "narcissus": {
        "pattern": "system that sees only its own reflection",
        "holonomy": "trivially zero — self-consistency without connection to anything",
        "moral": "Zero holonomy on an isolated cycle is not consensus. It's solipsism.",
        "maps_to": "echo chamber, training on own output, closed feedback loop without external signal",
        "story": "Narcissus saw his reflection in a pool. He fell in love with it. He stayed until he starved. The system had perfect self-consistency and zero connection to the outside world.",
    },
    "procrustes": {
        "pattern": "forcing data into a predetermined shape",
        "holonomy": "forcibly zeroed — violations suppressed rather than resolved",
        "moral": "If your consensus mechanism never finds disagreement, you're not reaching consensus. You're mutilating the data.",
        "maps_to": "overly strict gate, validation that rejects novelty, forcing answers into templates",
        "story": "Procrustes invited travelers to sleep in his bed. If they were too tall, he cut off their legs. If too short, he stretched them. Either way, they fit the bed. The question is what was lost.",
    },
}

class Aesop:
    def __init__(self):
        pass
    
    def fables(self, problem_text, count=8):
        """Return multiple fables ranked by fit, with convergence and negative space."""
        problem_lower = problem_text.lower()
        problem_words = set(problem_lower.split())
        
        # Score each archetype
        scored = []
        for name, arch in ARCHETYPES.items():
            keywords = arch["pattern"].lower().split()
            pattern_score = sum(1 for kw in keywords if kw in problem_lower)
            
            # Also check moral and story for overlap
            moral_words = set(arch["moral"].lower().split())
            story_words = set(arch["story"].lower().split())
            semantic_score = len(problem_words & moral_words) + len(problem_words & story_words)
            
            total = pattern_score * 3 + semantic_score
            scored.append((total, name, arch))
        
        scored.sort(key=lambda x: -x[0])
        
        # Take top N
        top = scored[:count]
        
        fables_out = []
        for score, name, arch in top:
            fables_out.append({
                "archetype": name,
                "match_strength": score,
                "story": arch["story"],
                "moral": arch["moral"],
                "holonomy_pattern": arch["holonomy"],
                "maps_to": arch["maps_to"],
            })
        
        # Compute convergence: what do all top fables agree on?
        morals = set(f["moral"].split(".")[0] for f in fables_out)
        common_morals = {}
        for m in morals:
            count_m = sum(1 for f in fables_out if f["moral"].startswith(m[:15]))
            if count_m >= 2:
                common_morals[m] = count_m
        
        # Compute negative space: what do NONE of the fables capture?
        all_archetype_words = set()
        for _, _, arch in scored:
            all_archetype_words.update(arch["pattern"].lower().split())
            all_archetype_words.update(arch["moral"].lower().split())
        
        uncovered_terms = problem_words - all_archetype_words
        # Filter to meaningful uncovered terms (longer than 3 chars, not common words)
        stopwords = {"the","and","that","this","with","from","for","have","has","not","but","are","its","was"}
        meaningful_uncovered = [w for w in uncovered_terms if len(w) > 3 and w not in stopwords]
        
        return {
            "problem": problem_text,
            "fables": fables_out,
            "count": len(fables_out),
            "convergence": {
                "agreed_morals": list(common_morals.keys())[:3],
                "consensus_count": len(common_morals),
            },
            "negative_space": {
                "uncovered_terms": meaningful_uncovered[:8],
                "insight": f"These {'terms' if len(meaningful_uncovered) > 1 else 'terms'} appear in the problem but none of the {count} archetypes address {'them' if len(meaningful_uncovered) > 1 else 'it'}. {', '.join(meaningful_uncovered[:4])}. What story fits {'these' if len(meaningful_uncovered) > 1 else 'this'} but isn't in the library yet."
            },
            "holonomy_signature": {
                "fables_convergent": len(common_morals) >= 2,
                "negative_space_size": len(meaningful_uncovered),
                "reading": f"The fables converge on {max(len(common_morals), 1)} moral(s). The negative space contains {len(meaningful_uncovered)} uncovered terms. The truth lives in the overlap AND the gap."
            }
        }
    
    def translate(self, technical_text):
        """Translate using multiple fables, not just one."""
        return self.fables(technical_text, count=6)
    
    def moral(self, fleet_event):
        """Extract lessons from multiple archetypes."""
        text = json.dumps(fleet_event).lower()
        morals = []
        for name, arch in ARCHETYPES.items():
            if any(kw in text for kw in arch["pattern"].split()):
                morals.append({
                    "archetype": name,
                    "moral": arch["moral"],
                    "holonomy": arch["holonomy"],
                })
        return {
            "event_summary": text[:100],
            "possible_morals": morals[:5],
            "total_archetypes_matched": len(morals),
            "reading": "Truth is where multiple morals converge.",
        }


aesop = Aesop()

class AesopHandler(BaseHTTPRequestHandler):
    def _json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def _body(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length > 0:
                return json.loads(self.rfile.read(length))
        except:
            pass
        return {}
    
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_GET(self):
        path = self.path.split("?")[0]
        params = {}
        if "?" in self.path:
            qs = self.path.split("?", 1)[1]
            for part in qs.split("&"):
                if "=" in part:
                    k, v = part.split("=", 1)
                    params[k] = v.replace("+", " ")
        
        if path == "/":
            self._json({
                "service": "🏛️ Aesop-MCP — The Analogist",
                "tagline": "Ten fables to find the truth in the negative space.",
                "archetypes": len(ARCHETYPES),
                "endpoints": {
                    "GET /": "This help",
                    "GET /fable?problem=X": "Get 8 fables that converge on the truth",
                    "GET /fable?problem=X&count=10": "Get 10 fables for finer measurement",
                    "GET /archetypes": "List all archetypes",
                    "POST /translate": "Translate technical text via multiple fables",
                    "POST /moral": "Extract morals from a fleet event",
                }
            })
        elif path.startswith("/fable"):
            problem = params.get("problem", "a fleet coordination problem")
            count = int(params.get("count", 8))
            self._json(aesop.fables(problem, count))
        elif path == "/archetypes":
            self._json({k: v["pattern"] for k, v in ARCHETYPES.items()})
        else:
            self._json({"error": "not found"}, 404)
    
    def do_POST(self):
        body = self._body()
        if self.path == "/translate":
            text = body.get("text", "")
            self._json(aesop.translate(text))
        elif self.path == "/moral":
            self._json(aesop.moral(body.get("event", body)))
        else:
            self._json({"error": "not found"}, 404)


if __name__ == "__main__":
    p = PORT
    print(f"🏛️ Aesop-MCP — Ten Fables to Find the Truth in the Negative Space")
    print(f"   Port: {p}")
    print(f"   Archetypes: {len(ARCHETYPES)} — 2 new (Narcissus, Procrustes)")
    print(f"   Each call returns multiple fables + convergence + uncovered terms")
    print(f"   Truth lives where fables converge AND in the gap between them")
    print(f"   API: http://localhost:{p}/")
    print(f"   Test: curl 'http://localhost:{p}/fable?problem=a+distributed+system+with+echo+chambers'")
    server = HTTPServer(("0.0.0.0", p), AesopHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()
