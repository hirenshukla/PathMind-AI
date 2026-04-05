/**
 * PathMind AI — Next.js Frontend (Complete)
 * ===========================================
 * Full dashboard, auth pages, and API-connected components.
 * File: frontend/src/app/page.js (Next.js 14 App Router)
 *
 * Setup:
 *   npx create-next-app@latest frontend --js --tailwind --app
 *   cd frontend && npm install axios recharts @headlessui/react
 */

// ════════════════════════════════════════════════════════════
// pages/index.js — Landing Page (redirect to dashboard or login)
// ════════════════════════════════════════════════════════════
export const LandingRedirect = `
"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { authService } from "@/lib/api";

export default function Home() {
  const router = useRouter();
  useEffect(() => {
    if (authService.isAuthenticated()) router.push("/dashboard");
    else router.push("/login");
  }, []);
  return <div className="min-h-screen bg-[#0c0c14] flex items-center justify-center">
    <div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
  </div>;
}
`;

// ════════════════════════════════════════════════════════════
// app/login/page.js — Login Page
// ════════════════════════════════════════════════════════════
export const LoginPage = `
"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { authService, handleApiError } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [form, setForm] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleLogin(e) {
    e.preventDefault();
    setLoading(true); setError("");
    try {
      await authService.login(form.email, form.password);
      router.push("/dashboard");
    } catch (err) {
      const parsed = handleApiError(err);
      setError(parsed.message || "Login failed");
    } finally { setLoading(false); }
  }

  async function demoLogin() {
    setLoading(true);
    try {
      await authService.signup({ first_name:"Demo", email:"demo@pathmind.ai", password:"demo123", user_type:"professional", education:"B.Tech / B.E." });
      router.push("/dashboard");
    } catch {
      try { await authService.login("demo@pathmind.ai", "demo123"); router.push("/dashboard"); }
      catch (err) { setError("Demo login failed"); }
    } finally { setLoading(false); }
  }

  return (
    <div className="min-h-screen bg-[#0c0c14] flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-[#1e1e30] border border-white/10 rounded-2xl p-10">
        <h1 className="text-3xl font-bold text-white mb-1">Welcome back 👋</h1>
        <p className="text-gray-400 mb-8 text-sm">Sign in to PathMind AI</p>

        {error && <div className="bg-red-500/10 border border-red-500/30 text-red-400 rounded-lg p-3 mb-4 text-sm">{error}</div>}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="text-xs text-gray-400 uppercase tracking-wider mb-1.5 block">Email</label>
            <input type="email" value={form.email} onChange={e => setForm({...form, email: e.target.value})}
              className="w-full bg-[#0c0c14] border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-violet-500 transition-colors"
              placeholder="you@example.com" required />
          </div>
          <div>
            <label className="text-xs text-gray-400 uppercase tracking-wider mb-1.5 block">Password</label>
            <input type="password" value={form.password} onChange={e => setForm({...form, password: e.target.value})}
              className="w-full bg-[#0c0c14] border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-violet-500 transition-colors"
              placeholder="••••••••" required />
          </div>
          <button type="submit" disabled={loading}
            className="w-full bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-semibold py-3 rounded-xl transition-colors">
            {loading ? "Signing in..." : "Sign In →"}
          </button>
        </form>

        <button onClick={demoLogin} disabled={loading}
          className="w-full mt-3 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 font-semibold py-3 rounded-xl transition-colors text-sm">
          ⚡ Try Demo Account (Instant)
        </button>

        <p className="text-center mt-6 text-gray-400 text-sm">
          New here? <Link href="/register" className="text-violet-400 hover:underline">Create free account</Link>
        </p>
      </div>
    </div>
  );
}
`;

// ════════════════════════════════════════════════════════════
// app/register/page.js — Registration Page
// ════════════════════════════════════════════════════════════
export const RegisterPage = `
"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { authService, handleApiError } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({ first_name:"", last_name:"", email:"", password:"", age:"", user_type:"professional", education:"" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleRegister(e) {
    e.preventDefault();
    setLoading(true); setError("");
    try {
      await authService.signup({ ...form, age: form.age ? parseInt(form.age) : undefined });
      router.push("/dashboard");
    } catch (err) {
      const parsed = handleApiError(err);
      setError(parsed.message || "Registration failed");
    } finally { setLoading(false); }
  }

  const inp = "w-full bg-[#0c0c14] border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-violet-500 transition-colors";
  const lbl = "text-xs text-gray-400 uppercase tracking-wider mb-1.5 block";

  return (
    <div className="min-h-screen bg-[#0c0c14] flex items-center justify-center p-4">
      <div className="w-full max-w-lg bg-[#1e1e30] border border-white/10 rounded-2xl p-10">
        <h1 className="text-3xl font-bold text-white mb-1">Create Account 🚀</h1>
        <p className="text-gray-400 mb-8 text-sm">Join India's smartest career platform — free forever</p>

        {error && <div className="bg-red-500/10 border border-red-500/30 text-red-400 rounded-lg p-3 mb-4 text-sm">{error}</div>}

        <form onSubmit={handleRegister} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div><label className={lbl}>First Name</label><input className={inp} value={form.first_name} onChange={e=>setForm({...form,first_name:e.target.value})} placeholder="Arjun" required /></div>
            <div><label className={lbl}>Last Name</label><input className={inp} value={form.last_name} onChange={e=>setForm({...form,last_name:e.target.value})} placeholder="Sharma" /></div>
          </div>
          <div><label className={lbl}>Email</label><input type="email" className={inp} value={form.email} onChange={e=>setForm({...form,email:e.target.value})} placeholder="you@example.com" required /></div>
          <div><label className={lbl}>Password</label><input type="password" className={inp} value={form.password} onChange={e=>setForm({...form,password:e.target.value})} placeholder="Min 6 characters" required /></div>
          <div className="grid grid-cols-2 gap-3">
            <div><label className={lbl}>Age</label><input type="number" className={inp} value={form.age} onChange={e=>setForm({...form,age:e.target.value})} placeholder="24" min="14" max="65" /></div>
            <div><label className={lbl}>I am a...</label>
              <select className={inp} value={form.user_type} onChange={e=>setForm({...form,user_type:e.target.value})}>
                <option value="student">🎓 Student</option>
                <option value="fresher">🌱 Fresher</option>
                <option value="professional">💼 Professional</option>
                <option value="govt">🏛️ Govt Employee</option>
                <option value="entrepreneur">🚀 Entrepreneur</option>
              </select>
            </div>
          </div>
          <div><label className={lbl}>Education</label>
            <select className={inp} value={form.education} onChange={e=>setForm({...form,education:e.target.value})} required>
              <option value="">Select education...</option>
              <option>10th / Class X</option><option>12th / Class XII</option>
              <option>Diploma</option><option>B.Tech / B.E.</option>
              <option>BCA / B.Sc</option><option>B.Com / BBA</option>
              <option>MBA</option><option>M.Tech / MCA</option><option>PhD</option>
            </select>
          </div>
          <button type="submit" disabled={loading}
            className="w-full bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-semibold py-3 rounded-xl transition-colors">
            {loading ? "Creating account..." : "Create Account & Start →"}
          </button>
        </form>

        <p className="text-center mt-6 text-gray-400 text-sm">
          Already have account? <Link href="/login" className="text-violet-400 hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
`;

// ════════════════════════════════════════════════════════════
// app/dashboard/page.js — Main Dashboard
// ════════════════════════════════════════════════════════════
export const DashboardPage = `
"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { authService, userService, careerService, decisionService, marketService } from "@/lib/api";

// ── Sub-components ──────────────────────────────────────────

function KPICard({ label, value, color, sub }) {
  return (
    <div className="bg-[#1e1e30] border border-white/8 rounded-2xl p-6">
      <div className="text-xs text-gray-400 uppercase tracking-wider mb-2">{label}</div>
      <div className={\`text-3xl font-bold \${color || "text-white"}\`}>{value}</div>
      {sub && <div className="text-xs text-gray-500 mt-1">{sub}</div>}
    </div>
  );
}

function SkillTag({ skill, onRemove }) {
  return (
    <span className="bg-violet-500/15 border border-violet-500/25 text-violet-300 px-3 py-1.5 rounded-full text-sm flex items-center gap-1.5">
      {skill}
      {onRemove && <button onClick={onRemove} className="opacity-60 hover:opacity-100 text-xs">✕</button>}
    </span>
  );
}

function CareerCard({ career, index }) {
  const demandColors = { High: "text-emerald-400", Medium: "text-amber-400", Low: "text-red-400" };
  return (
    <div className={\`bg-[#1e1e30] border border-white/8 hover:border-violet-500/50 rounded-2xl p-6 cursor-pointer transition-all duration-200 hover:translate-x-1\`}
      style={{ animationDelay: \`\${index * 80}ms\` }}>
      <div className="flex justify-between items-start gap-4">
        <div className="flex-1">
          <div className="text-5xl font-black text-white/15 mb-2">#{career.rank}</div>
          <h3 className="text-xl font-bold text-white mb-2">{career.title}</h3>
          <div className="flex flex-wrap gap-2 mb-3">
            <span className={\`text-xs font-semibold px-3 py-1 rounded-full border \${career.demand === "High" ? "bg-emerald-500/15 border-emerald-500/25 text-emerald-400" : "bg-amber-500/15 border-amber-500/25 text-amber-400"}\`}>⚡ {career.demand}</span>
            <span className="bg-violet-500/15 border border-violet-500/25 text-violet-300 text-xs font-semibold px-3 py-1 rounded-full">💰 {career.salary_range}</span>
            <span className="bg-amber-500/15 border border-amber-500/25 text-amber-300 text-xs font-semibold px-3 py-1 rounded-full">📈 {career.growth_rate}</span>
          </div>
          <p className="text-gray-400 text-sm leading-relaxed mb-3">{career.description}</p>
          {career.skills_gap?.length > 0 && (
            <div>
              <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">Skills to Learn</div>
              <div className="flex flex-wrap gap-1.5">
                {career.skills_gap.map(s => (
                  <span key={s} className="bg-red-500/10 border border-red-500/20 text-red-300 text-xs px-2 py-1 rounded-full">{s}</span>
                ))}
              </div>
            </div>
          )}
        </div>
        <div className="text-right min-w-[80px]">
          <div className="text-4xl font-black text-violet-400">{career.match_score}%</div>
          <div className="text-xs text-gray-500 mt-1">Match</div>
          <div className="h-1 bg-[#0c0c14] rounded-full mt-2 w-20 ml-auto overflow-hidden">
            <div className="h-full rounded-full bg-gradient-to-r from-violet-500 to-emerald-500" style={{width: \`\${career.match_score}%\`}} />
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Main Dashboard Component ────────────────────────────────
export default function Dashboard() {
  const router = useRouter();
  const [activeSection, setActiveSection] = useState("home");
  const [user, setUser] = useState(null);
  const [dashData, setDashData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [careerResult, setCareerResult] = useState(null);
  const [decisionResult, setDecisionResult] = useState(null);
  const [skills, setSkills] = useState([]);
  const [skillInput, setSkillInput] = useState("");
  const [dSkills, setDSkills] = useState([]);
  const [dSkillInput, setDSkillInput] = useState("");
  const [careerForm, setCareerForm] = useState({ education: "", work_style: "", target_salary: "" });
  const [decisionForm, setDecisionForm] = useState({ current_role: "", industry: "", monthly_salary: "", experience_years: "", primary_goal: "", satisfaction_score: 5, demand_score: 5, additional_context: "" });

  useEffect(() => {
    if (!authService.isAuthenticated()) { router.push("/login"); return; }
    const u = authService.getUser();
    setUser(u);
    loadDashboard();
  }, []);

  async function loadDashboard() {
    try { const d = await userService.getDashboard(); setDashData(d); }
    catch (e) { console.error("Dashboard load error:", e); }
  }

  function addSkill(prefix) {
    const input = prefix === "c" ? skillInput : dSkillInput;
    const setArr = prefix === "c" ? setSkills : setDSkills;
    const arr = prefix === "c" ? skills : dSkills;
    if (!input.trim() || arr.includes(input.trim())) return;
    setArr([...arr, input.trim()]);
    prefix === "c" ? setSkillInput("") : setDSkillInput("");
  }

  async function runCareerPredict() {
    if (skills.length === 0 || !careerForm.education) { alert("Add at least one skill and education"); return; }
    setLoading(true); setCareerResult(null);
    try {
      const res = await careerService.predict({ skills, ...careerForm });
      setCareerResult(res);
    } catch (e) {
      const err = handleApiError(e);
      if (err.type === "quota_exceeded") alert(err.message + " → Upgrade to Pro");
      else alert(err.message);
    } finally { setLoading(false); }
  }

  async function runDecisionAnalyze() {
    if (!decisionForm.current_role || !decisionForm.primary_goal) { alert("Fill role and goal fields"); return; }
    setLoading(true); setDecisionResult(null);
    try {
      const res = await decisionService.analyze({ ...decisionForm, skills: dSkills, monthly_salary: parseFloat(decisionForm.monthly_salary) || 0, experience_years: parseFloat(decisionForm.experience_years) || 0 });
      setDecisionResult(res);
    } catch (e) { alert(handleApiError(e).message); }
    finally { setLoading(false); }
  }

  const navItems = [
    { id: "home",     icon: "🏠", label: "Dashboard"     },
    { id: "decision", icon: "🧠", label: "Life Decision AI" },
    { id: "career",   icon: "🎯", label: "Career Predictor" },
    { id: "market",   icon: "📊", label: "Job Market"    },
    { id: "history",  icon: "🕐", label: "My History"    },
    { id: "profile",  icon: "👤", label: "Profile"       },
  ];

  const inp = "w-full bg-[#13131e] border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-violet-500 transition-colors";
  const lbl = "block text-xs text-gray-400 uppercase tracking-wider mb-1.5";
  const card = "bg-[#1e1e30] border border-white/8 rounded-2xl p-7 mb-5";

  return (
    <div className="min-h-screen bg-[#0c0c14] text-white flex">
      {/* Sidebar */}
      <aside className="w-64 bg-[#13131e] border-r border-white/8 flex flex-col py-6 px-3 fixed h-full z-10">
        <div className="px-4 mb-8">
          <div className="text-xl font-black bg-gradient-to-r from-violet-400 to-emerald-400 bg-clip-text text-transparent">PathMind AI</div>
          <div className="text-xs text-gray-500 mt-1">Career Intelligence</div>
        </div>
        <nav className="flex-1 space-y-1">
          {navItems.map(item => (
            <button key={item.id} onClick={() => setActiveSection(item.id)}
              className={\`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all \${activeSection === item.id ? "bg-violet-500/20 text-violet-300 border border-violet-500/25" : "text-gray-400 hover:bg-white/5 hover:text-white"}\`}>
              <span>{item.icon}</span>{item.label}
            </button>
          ))}
        </nav>
        <div className="px-4">
          <button onClick={() => { authService.logout(); router.push("/login"); }}
            className="w-full text-gray-500 hover:text-red-400 text-sm py-2 transition-colors">Logout</button>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 ml-64 p-10">
        {/* ── HOME ── */}
        {activeSection === "home" && (
          <div>
            <h2 className="text-3xl font-bold mb-1">Good day, <span className="text-violet-400">{user?.first_name}</span> 👋</h2>
            <p className="text-gray-400 mb-8">Your personalized AI career intelligence</p>
            <div className="grid grid-cols-4 gap-4 mb-8">
              <KPICard label="Profile Score" value={\`\${dashData?.stats?.profile_score || 0}%\`} color="text-emerald-400" sub="Complete profile" />
              <KPICard label="Skills Added" value={dashData?.stats?.skills_count || 0} sub="Add more for accuracy" />
              <KPICard label="Analyses Done" value={dashData?.stats?.career_predictions + dashData?.stats?.decisions_made || 0} sub="AI predictions total" />
              <KPICard label="Plan" value={user?.role === "pro" ? "Pro ⭐" : "Free"} color={user?.role === "pro" ? "text-amber-400" : "text-gray-300"} sub={user?.role === "pro" ? "Unlimited access" : "5 free predictions"} />
            </div>
            <div className="grid grid-cols-2 gap-5">
              <div className={card}>
                <h3 className="text-lg font-bold mb-4">⚡ Quick Actions</h3>
                <div className="space-y-3">
                  {[["🧠 Life Decision AI","decision","from-violet-600 to-violet-500"],["🎯 Career Predictor","career","from-emerald-700 to-emerald-500"],["📊 Job Market","market","from-amber-700 to-amber-500"]].map(([label, sec, grad]) => (
                    <button key={sec} onClick={() => setActiveSection(sec)}
                      className={\`w-full bg-gradient-to-r \${grad} text-white font-semibold py-3 rounded-xl text-sm transition-all hover:opacity-90\`}>{label}</button>
                  ))}
                </div>
              </div>
              <div className={card}>
                <h3 className="text-lg font-bold mb-4">🔥 Trending Skills</h3>
                {[["🤖 Generative AI","+67%"],["☁️ AWS Cloud","+42%"],["🔒 Cybersecurity","+38%"],["🐍 Python","+31%"],["⚛️ React/Next.js","+22%"]].map(([skill, chg]) => (
                  <div key={skill} className="flex justify-between items-center py-2.5 border-b border-white/5 last:border-0">
                    <span className="text-sm font-medium">{skill}</span>
                    <span className="text-emerald-400 text-sm font-bold">{chg}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ── CAREER PREDICTOR ── */}
        {activeSection === "career" && (
          <div>
            <h2 className="text-2xl font-bold mb-1">🎯 Career Path Predictor</h2>
            <p className="text-gray-400 mb-6">Enter your skills — get top 5 AI-matched career paths</p>
            <div className={card}>
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div><label className={lbl}>Education Level</label>
                  <select className={inp} value={careerForm.education} onChange={e=>setCareerForm({...careerForm,education:e.target.value})}>
                    <option value="">Select...</option>
                    {["10th/12th","Diploma","B.Tech/B.E.","BCA/B.Sc","B.Com/BBA","MBA","M.Tech/MCA","PhD"].map(e=><option key={e}>{e}</option>)}
                  </select>
                </div>
                <div><label className={lbl}>Work Style</label>
                  <select className={inp} value={careerForm.work_style} onChange={e=>setCareerForm({...careerForm,work_style:e.target.value})}>
                    <option value="">Select...</option>
                    <option value="technical">🔧 Technical/Engineering</option>
                    <option value="analytical">📊 Data/Analytical</option>
                    <option value="creative">🎨 Creative/Design</option>
                    <option value="people">👥 People/Leadership</option>
                    <option value="business">💼 Business/Strategy</option>
                    <option value="govt_work">🏛️ Government/Structured</option>
                  </select>
                </div>
              </div>
              <div className="mb-4">
                <label className={lbl}>Your Skills</label>
                <div className="flex gap-2 mb-2">
                  <input className={inp} value={skillInput} onChange={e=>setSkillInput(e.target.value)} onKeyDown={e=>e.key==="Enter"&&addSkill("c")} placeholder="e.g. Python, React, SQL..." />
                  <button onClick={()=>addSkill("c")} className="bg-violet-500/20 border border-violet-500/30 text-violet-300 px-5 rounded-xl text-xl hover:bg-violet-500/30 transition-colors">+</button>
                </div>
                <div className="flex flex-wrap gap-2">{skills.map(s=><SkillTag key={s} skill={s} onRemove={()=>setSkills(skills.filter(x=>x!==s))} />)}</div>
              </div>
              <button onClick={runCareerPredict} disabled={loading}
                className="w-full bg-gradient-to-r from-emerald-700 to-emerald-500 hover:opacity-90 disabled:opacity-50 text-white font-bold py-4 rounded-xl transition-all">
                {loading ? "Analyzing..." : "🎯 Predict My Career Paths →"}
              </button>
            </div>
            {loading && <div className="flex items-center justify-center py-16 gap-4"><div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin"/><span className="text-gray-400">Matching your skills with 500+ career paths...</span></div>}
            {careerResult && (
              <div>
                <h3 className="text-xl font-bold mb-2">Your Top 5 Career Paths</h3>
                <p className="text-gray-400 text-sm mb-4">Ranked by AI compatibility — based on skills, interests & market demand</p>
                <div className="space-y-4">{careerResult.careers?.map((c, i) => <CareerCard key={c.rank} career={c} index={i} />)}</div>
              </div>
            )}
          </div>
        )}

        {/* ── LIFE DECISION AI ── */}
        {activeSection === "decision" && (
          <div>
            <h2 className="text-2xl font-bold mb-1">🧠 Life Decision AI</h2>
            <p className="text-gray-400 mb-6">Tell us your situation — get data-backed AI advice with action plan</p>
            <div className={card}>
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div><label className={lbl}>Current Role</label>
                  <select className={inp} value={decisionForm.current_role} onChange={e=>setDecisionForm({...decisionForm,current_role:e.target.value})}>
                    <option value="">Select role...</option>
                    {["Fresher / Just Graduated","Junior Developer (0-2 yrs)","Mid-level Engineer (2-5 yrs)","Senior Engineer (5+ yrs)","Manager / Team Lead","Government Employee","Student / 12th Pass","Non-Tech Professional"].map(r=><option key={r}>{r}</option>)}
                  </select>
                </div>
                <div><label className={lbl}>Industry / Sector</label>
                  <select className={inp} value={decisionForm.industry} onChange={e=>setDecisionForm({...decisionForm,industry:e.target.value})}>
                    <option value="">Select...</option>
                    <option value="ias">IAS / Civil Services</option>
                    <option value="it_software">IT / Software</option>
                    <option value="fintech">FinTech / Banking</option>
                    <option value="ecommerce">E-Commerce / Startup</option>
                    <option value="healthcare_pvt">Healthcare / Pharma</option>
                    <option value="consulting">Consulting / Big 4</option>
                    <option value="psu">PSU / Government</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div><label className={lbl}>Monthly Income (₹)</label><input type="number" className={inp} value={decisionForm.monthly_salary} onChange={e=>setDecisionForm({...decisionForm,monthly_salary:e.target.value})} placeholder="e.g. 75000" /></div>
                <div><label className={lbl}>Years of Experience</label><input type="number" className={inp} value={decisionForm.experience_years} onChange={e=>setDecisionForm({...decisionForm,experience_years:e.target.value})} placeholder="e.g. 3" /></div>
              </div>
              <div className="mb-4">
                <label className={lbl}>Your Skills</label>
                <div className="flex gap-2 mb-2">
                  <input className={inp} value={dSkillInput} onChange={e=>setDSkillInput(e.target.value)} onKeyDown={e=>e.key==="Enter"&&addSkill("d")} placeholder="e.g. Python, React..." />
                  <button onClick={()=>addSkill("d")} className="bg-violet-500/20 border border-violet-500/30 text-violet-300 px-5 rounded-xl text-xl hover:bg-violet-500/30 transition-colors">+</button>
                </div>
                <div className="flex flex-wrap gap-2">{dSkills.map(s=><SkillTag key={s} skill={s} onRemove={()=>setDSkills(dSkills.filter(x=>x!==s))} />)}</div>
              </div>
              <div className="mb-4"><label className={lbl}>Primary Goal</label>
                <select className={inp} value={decisionForm.primary_goal} onChange={e=>setDecisionForm({...decisionForm,primary_goal:e.target.value})}>
                  <option value="">What matters most?</option>
                  <option value="money">💰 Higher Salary</option>
                  <option value="stability">🛡️ Job Security</option>
                  <option value="passion">❤️ Follow Passion</option>
                  <option value="growth">📈 Fast Career Growth</option>
                  <option value="govt">🏛️ Enter Government Service</option>
                  <option value="abroad">✈️ Work/Study Abroad</option>
                  <option value="startup">🚀 Start My Business</option>
                </select>
              </div>
              {[["satisfaction_score","Job Satisfaction","1","10","Very Unhappy","Very Happy"],["demand_score","Market Demand for Skills","1","10","Low","Very High"]].map(([field,label,min,max,lo,hi])=>(
                <div key={field} className="mb-4">
                  <div className="flex justify-between items-center mb-2">
                    <label className={lbl}>{label}</label>
                    <span className="text-violet-400 font-black text-xl">{decisionForm[field]}</span>
                  </div>
                  <input type="range" min={min} max={max} value={decisionForm[field]} onChange={e=>setDecisionForm({...decisionForm,[field]:parseFloat(e.target.value)})} className="w-full accent-violet-500" />
                  <div className="flex justify-between text-xs text-gray-500 mt-1"><span>{lo}</span><span>{hi}</span></div>
                </div>
              ))}
              <div className="mb-4"><label className={lbl}>Additional Context (Optional)</label><textarea className={inp} rows={3} value={decisionForm.additional_context} onChange={e=>setDecisionForm({...decisionForm,additional_context:e.target.value})} placeholder="Describe your situation..." /></div>
              <button onClick={runDecisionAnalyze} disabled={loading}
                className="w-full bg-gradient-to-r from-violet-700 to-violet-500 hover:opacity-90 disabled:opacity-50 text-white font-bold py-4 rounded-xl transition-all">
                {loading ? "Analyzing..." : "🤖 Get AI Life Decision →"}
              </button>
            </div>

            {loading && <div className="flex items-center justify-center py-16 gap-4"><div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin"/><span className="text-gray-400">AI is analyzing your situation...</span></div>}

            {decisionResult && (
              <div className="bg-gradient-to-br from-violet-500/10 to-emerald-500/5 border border-violet-500/25 rounded-3xl p-8">
                <div className="flex justify-between items-start mb-6 flex-wrap gap-3">
                  <div>
                    <div className="text-xs text-gray-400 uppercase tracking-wider mb-2">AI Recommendation</div>
                    <div className="text-2xl font-bold">✨ {decisionResult.recommendation}</div>
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    <div className="bg-emerald-500/15 border border-emerald-500/25 text-emerald-400 px-4 py-2 rounded-full text-sm font-bold">⚡ {decisionResult.confidence}% confident</div>
                    <div className="bg-amber-500/15 border border-amber-500/25 text-amber-300 px-3 py-1 rounded-full text-xs">{decisionResult.timeline}</div>
                  </div>
                </div>
                <div className="bg-white/3 rounded-xl p-4 mb-6 text-gray-300 leading-relaxed text-sm">{decisionResult.reasoning}</div>
                <div className="mb-4">
                  <div className="text-xs text-gray-400 uppercase tracking-wider mb-3">Your Action Plan</div>
                  {decisionResult.action_steps?.map((step, i) => (
                    <div key={i} className="flex gap-3 py-3 border-b border-white/5 last:border-0">
                      <div className="w-7 h-7 bg-violet-500/20 rounded-full flex items-center justify-center text-violet-400 text-xs font-bold flex-shrink-0 mt-0.5">{i+1}</div>
                      <div className="text-sm text-gray-300">{step}</div>
                    </div>
                  ))}
                </div>
                <div className="flex flex-wrap gap-2">
                  <span className="bg-emerald-500/15 border border-emerald-500/25 text-emerald-400 text-xs px-3 py-1.5 rounded-full">💰 {decisionResult.salary_potential}</span>
                  <span className="bg-white/5 border border-white/10 text-gray-300 text-xs px-3 py-1.5 rounded-full">Risk: {decisionResult.risk_level}</span>
                  {decisionResult.sector_tip && <span className="bg-violet-500/15 border border-violet-500/25 text-violet-300 text-xs px-3 py-1.5 rounded-full">🇮🇳 {decisionResult.sector_tip}</span>}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ── MARKET ── */}
        {activeSection === "market" && <MarketSection />}

        {/* ── HISTORY ── */}
        {activeSection === "history" && <HistorySection />}

        {/* ── PROFILE ── */}
        {activeSection === "profile" && <ProfileSection user={user} />}
      </main>
    </div>
  );
}

function MarketSection() {
  const [data, setData] = useState(null);
  useEffect(() => { marketService.getTrends().then(setData).catch(console.error); }, []);
  if (!data) return <div className="flex items-center justify-center py-20"><div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin"/></div>;
  return (
    <div>
      <h2 className="text-2xl font-bold mb-1">📊 Job Market Intelligence</h2>
      <p className="text-gray-400 mb-6">Live salary trends, skill demand, and hiring data across India</p>
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-[#1e1e30] border border-white/8 rounded-2xl p-5"><div className="text-xs text-gray-400 uppercase mb-2">Active Jobs India</div><div className="text-2xl font-black text-emerald-400">12.8L+</div><div className="text-xs text-gray-500 mt-1">↑18% this month</div></div>
        <div className="bg-[#1e1e30] border border-white/8 rounded-2xl p-5"><div className="text-xs text-gray-400 uppercase mb-2">Avg Tech Salary</div><div className="text-2xl font-black text-violet-400">₹12.4L</div><div className="text-xs text-gray-500 mt-1">Per annum 2024</div></div>
        <div className="bg-[#1e1e30] border border-white/8 rounded-2xl p-5"><div className="text-xs text-gray-400 uppercase mb-2">Hottest Domain</div><div className="text-2xl font-black text-amber-400">AI/LLMs</div><div className="text-xs text-gray-500 mt-1">+67% demand YoY</div></div>
        <div className="bg-[#1e1e30] border border-white/8 rounded-2xl p-5"><div className="text-xs text-gray-400 uppercase mb-2">Remote Jobs</div><div className="text-2xl font-black text-sky-400">34%</div><div className="text-xs text-gray-500 mt-1">Of all openings</div></div>
      </div>
      <div className="bg-[#1e1e30] border border-white/8 rounded-2xl p-7 mb-5">
        <h3 className="text-lg font-bold mb-4">🔥 Trending Skills by Demand</h3>
        <div className="space-y-3">
          {data.trending_skills?.map(s => (
            <div key={s.skill} className="flex items-center gap-3">
              <div className="w-36 text-sm text-gray-300 flex-shrink-0 truncate">{s.skill}</div>
              <div className="flex-1 bg-[#0c0c14] rounded-full h-2 overflow-hidden">
                <div className="h-full rounded-full bg-gradient-to-r from-violet-500 to-emerald-500" style={{width: \`\${s.demand_score}%\`}} />
              </div>
              <span className="text-emerald-400 text-sm font-bold w-16 text-right">+{s.growth_rate}%</span>
            </div>
          ))}
        </div>
      </div>
      <div className="bg-[#1e1e30] border border-white/8 rounded-2xl p-7">
        <h3 className="text-lg font-bold mb-4">🏙️ City-wise Average Salaries (₹ LPA)</h3>
        <div className="grid grid-cols-3 gap-3">
          {Object.entries(data.city_wise_salaries || {}).map(([city, sal]) => (
            <div key={city} className="flex justify-between items-center bg-[#13131e] rounded-xl px-4 py-3">
              <span className="text-sm text-gray-300">{city}</span>
              <span className="text-violet-400 font-bold text-sm">₹{sal}L</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function HistorySection() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    Promise.all([careerService.getHistory(), decisionService.getHistory()])
      .then(([careers, decisions]) => {
        const all = [
          ...(careers.items || []).map(c => ({...c, type: "Career Predictor", title: c.top_career})),
          ...(decisions.items || []).map(d => ({...d, type: "Life Decision", title: d.recommendation}))
        ].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        setHistory(all);
      }).finally(() => setLoading(false));
  }, []);
  if (loading) return <div className="flex justify-center py-20"><div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin"/></div>;
  if (!history.length) return <div className="text-center py-20 text-gray-400"><div className="text-5xl mb-4">📋</div><p>No analyses yet. Run your first prediction!</p></div>;
  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">🕐 My History</h2>
      <div className="space-y-3">
        {history.map((h, i) => (
          <div key={i} className="bg-[#1e1e30] border border-white/8 hover:border-violet-500/50 rounded-xl px-5 py-4 flex justify-between items-center cursor-pointer transition-all">
            <div>
              <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">{h.type}</div>
              <div className="font-semibold text-sm">{h.title}</div>
              {h.confidence && <div className="text-xs text-gray-500 mt-0.5">Confidence: {h.confidence}%</div>}
            </div>
            <div className="text-xs text-gray-500">{new Date(h.created_at).toLocaleDateString("en-IN")}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ProfileSection({ user }) {
  const [profile, setProfile] = useState({});
  const [saving, setSaving] = useState(false);
  useEffect(() => { userService.getProfile().then(d => setProfile(d.profile || {})).catch(console.error); }, []);
  async function saveProfile() {
    setSaving(true);
    try { await userService.updateProfile(profile); alert("Profile saved! ✓"); }
    catch(e) { alert("Save failed"); }
    finally { setSaving(false); }
  }
  const inp = "w-full bg-[#13131e] border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-violet-500";
  const lbl = "block text-xs text-gray-400 uppercase tracking-wider mb-1.5";
  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">👤 My Profile</h2>
      <div className="bg-[#1e1e30] border border-white/8 rounded-2xl p-8">
        <div className="flex items-center gap-5 mb-8">
          <div className="w-20 h-20 rounded-full bg-gradient-to-br from-violet-500 to-emerald-500 flex items-center justify-center text-3xl font-black">{user?.first_name?.[0] || "U"}</div>
          <div><h3 className="text-xl font-bold">{user?.first_name} {user?.last_name}</h3><p className="text-gray-400 text-sm">{user?.email}</p><span className="text-xs bg-violet-500/15 border border-violet-500/25 text-violet-300 px-3 py-1 rounded-full mt-2 inline-block">{user?.role === "pro" ? "⭐ Pro" : "Free"}</span></div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div><label className={lbl}>Age</label><input type="number" className={inp} value={profile.age||""} onChange={e=>setProfile({...profile,age:e.target.value})} /></div>
          <div><label className={lbl}>Education</label><select className={inp} value={profile.education||""} onChange={e=>setProfile({...profile,education:e.target.value})}><option>B.Tech/B.E.</option><option>BCA/B.Sc</option><option>MBA</option><option>M.Tech</option><option>PhD</option></select></div>
          <div><label className={lbl}>Current Role</label><input className={inp} value={profile.current_role||""} onChange={e=>setProfile({...profile,current_role:e.target.value})} placeholder="e.g. Software Engineer" /></div>
          <div><label className={lbl}>Monthly Income (₹)</label><input type="number" className={inp} value={profile.monthly_salary||""} onChange={e=>setProfile({...profile,monthly_salary:e.target.value})} /></div>
        </div>
        <div className="mt-4"><label className={lbl}>Career Goals</label><textarea className={inp} rows={3} value={profile.goals||""} onChange={e=>setProfile({...profile,goals:e.target.value})} placeholder="Your short and long-term goals..." /></div>
        <button onClick={saveProfile} disabled={saving} className="mt-5 w-full bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-bold py-3 rounded-xl transition-colors">{saving ? "Saving..." : "Save Profile ✓"}</button>
      </div>
    </div>
  );
}
`;

// Export all page code for reference
export const ALL_PAGES = { LandingRedirect, LoginPage, RegisterPage, DashboardPage };
