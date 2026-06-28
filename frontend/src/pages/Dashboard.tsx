import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { api } from "../lib/api";
import { LogOut, CheckCircle2, XCircle, Loader2, Play, Send } from "lucide-react";
import { cn } from "../lib/utils";

export default function Dashboard() {
  const { user, logout, refreshUser } = useAuth();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [toast, setToast] = useState<{ type: "success" | "error"; message: string } | null>(null);

  const [isGenerating, setIsGenerating] = useState(false);
  const [isPublishing, setIsPublishing] = useState(false);
  const [generatedText, setGeneratedText] = useState("");

  // Handle OAuth Redirects
  useEffect(() => {
    const provider = searchParams.get("provider");
    const success = searchParams.get("success");
    
    if (provider && success) {
      if (success === "true") {
        setToast({ type: "success", message: `${provider.charAt(0).toUpperCase() + provider.slice(1)} connected successfully!` });
        refreshUser(); // Refresh user to get updated connected status
      } else {
        setToast({ type: "error", message: `Failed to connect ${provider}. Please try again.` });
      }
      // Remove query params
      setSearchParams({});
    }
  }, [searchParams, setSearchParams, refreshUser]);

  // Auto clear toast
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  const handleConnect = async (provider: "instagram" | "linkedin") => {
    try {
      const data = await api.get<{ login_url: string }>(`/${provider}/login`);
      window.location.href = data.login_url;
    } catch (err: any) {
      setToast({ type: "error", message: err.message || `Failed to start ${provider} login` });
    }
  };

  const handleGenerate = async () => {
    if (!user?.instagram_account_id) {
      setToast({ type: "error", message: "Please connect Instagram first." });
      return;
    }
    
    setIsGenerating(true);
    setToast(null);
    setGeneratedText("");
    
    try {
      const data = await api.post<{ linkedin_post: string; message: string }>("/generate");
      setGeneratedText(data.linkedin_post);
      setToast({ type: "success", message: data.message });
    } catch (err: any) {
      setToast({ type: "error", message: err.message || "Failed to generate post." });
    } finally {
      setIsGenerating(false);
    }
  };

  const handlePublish = async () => {
    if (!user?.linkedin_author_urn) {
      setToast({ type: "error", message: "Please connect LinkedIn first." });
      return;
    }
    if (!generatedText.trim()) {
      setToast({ type: "error", message: "Please generate or write a post first." });
      return;
    }
    
    setIsPublishing(true);
    try {
      const data = await api.post<{ message: string }>("/publish", { linkedin_post: generatedText });
      setToast({ type: "success", message: data.message });
      setGeneratedText(""); // Clear after success
    } catch (err: any) {
      setToast({ type: "error", message: err.message || "Failed to publish post." });
    } finally {
      setIsPublishing(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 font-sans pb-20">
      {/* Navbar */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-lg sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="font-bold text-xl bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-blue-400">
            PostMorph AI
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-slate-400 hidden sm:inline-block">{user?.email}</span>
            <button
              onClick={() => { logout(); navigate("/"); }}
              className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors flex items-center gap-2 text-sm"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 pt-10 space-y-12">
        
        {/* Toast Notification */}
        {toast && (
          <div className={cn(
            "fixed top-20 right-4 p-4 rounded-xl shadow-xl flex items-start gap-3 z-50 animate-in slide-in-from-right-10",
            toast.type === "success" ? "bg-emerald-950/80 border border-emerald-900 text-emerald-300" : "bg-red-950/80 border border-red-900 text-red-300"
          )}>
            {toast.type === "success" ? <CheckCircle2 className="w-5 h-5 shrink-0" /> : <XCircle className="w-5 h-5 shrink-0" />}
            <p className="text-sm pr-4">{toast.message}</p>
            <button onClick={() => setToast(null)} className="absolute top-4 right-2 text-current opacity-50 hover:opacity-100">
              <XCircle className="w-4 h-4" />
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Instagram Card */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 flex flex-col items-center text-center">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-yellow-500 via-pink-500 to-purple-600 p-[2px] mb-4">
              <div className="w-full h-full bg-slate-900 rounded-[14px] flex items-center justify-center">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <rect width="20" height="20" x="2" y="2" rx="5" ry="5" strokeWidth="2"/>
                  <path strokeWidth="2" d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/>
                  <line x1="17.5" x2="17.51" y1="6.5" y2="6.5" strokeWidth="2"/>
                </svg>
              </div>
            </div>
            <h3 className="text-xl font-semibold mb-2">Instagram Source</h3>
            <p className="text-sm text-slate-400 mb-6">Connect your business account to fetch your latest Reels.</p>
            
            {user?.instagram_account_id ? (
              <div className="inline-flex items-center gap-2 text-emerald-400 bg-emerald-950/50 px-4 py-2 rounded-full text-sm border border-emerald-900">
                <CheckCircle2 className="w-4 h-4" />
                Connected
              </div>
            ) : (
              <button
                onClick={() => handleConnect("instagram")}
                className="w-full px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl transition-colors text-sm font-medium border border-slate-700"
              >
                Connect Instagram
              </button>
            )}
          </div>

          {/* LinkedIn Card */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 flex flex-col items-center text-center">
            <div className="w-16 h-16 rounded-2xl bg-[#0077b5] flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">LinkedIn Destination</h3>
            <p className="text-sm text-slate-400 mb-6">Connect your profile to publish the AI-generated posts.</p>
            
            {user?.linkedin_author_urn ? (
              <div className="inline-flex items-center gap-2 text-emerald-400 bg-emerald-950/50 px-4 py-2 rounded-full text-sm border border-emerald-900">
                <CheckCircle2 className="w-4 h-4" />
                Connected
              </div>
            ) : (
              <button
                onClick={() => handleConnect("linkedin")}
                className="w-full px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl transition-colors text-sm font-medium border border-slate-700"
              >
                Connect LinkedIn
              </button>
            )}
          </div>
        </div>

        {/* Action Pipeline */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 lg:p-8">
          <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4 border-b border-slate-800 pb-8">
            <div>
              <h2 className="text-2xl font-bold">Automation Pipeline</h2>
              <p className="text-slate-400 text-sm mt-1">Generate a post from your latest Reel and publish it.</p>
              
              <div className="mt-4 flex items-center gap-3">
                <div className="flex items-center gap-2 text-sm bg-slate-950/50 px-3 py-1.5 rounded-full border border-slate-800">
                  <span className="relative flex h-2.5 w-2.5">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                  </span>
                  <span className="text-slate-300">Background Worker Active</span>
                </div>
                <button
                  onClick={async () => {
                    setToast({ type: "success", message: "Starting manual sync..." });
                    try {
                      const res = await api.post<{ summary: any }>("/automation/sync");
                      setToast({ type: "success", message: `Sync complete! Checked: ${res.summary.users_checked}, Published: ${res.summary.posts_published}` });
                    } catch (e: any) {
                      setToast({ type: "error", message: e.message || "Manual sync failed" });
                    }
                  }}
                  className="text-xs font-medium text-slate-300 bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded-full transition-colors"
                >
                  Sync Now
                </button>
              </div>
            </div>
            <button
              onClick={handleGenerate}
              disabled={isGenerating || !user?.instagram_account_id}
              className="inline-flex items-center justify-center px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-purple-900/20"
            >
              {isGenerating ? (
                <><Loader2 className="w-5 h-5 mr-2 animate-spin" /> Processing...</>
              ) : (
                <><Play className="w-5 h-5 mr-2" /> Generate Draft</>
              )}
            </button>
          </div>

          {/* Editor */}
          <div className="space-y-4">
            <label className="block text-sm font-medium text-slate-300">Generated Content</label>
            <textarea
              value={generatedText}
              onChange={(e) => setGeneratedText(e.target.value)}
              placeholder="Your AI generated LinkedIn post will appear here. You can edit it before publishing."
              className="w-full h-64 bg-slate-950/50 border border-slate-800 rounded-xl p-4 text-slate-200 focus:outline-none focus:ring-2 focus:ring-purple-500/50 resize-y"
            />
            
            <div className="flex justify-end">
              <button
                onClick={handlePublish}
                disabled={isPublishing || !generatedText.trim() || !user?.linkedin_author_urn}
                className="inline-flex items-center justify-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-900/20"
              >
                {isPublishing ? (
                  <><Loader2 className="w-5 h-5 mr-2 animate-spin" /> Publishing...</>
                ) : (
                  <><Send className="w-5 h-5 mr-2" /> Publish to LinkedIn</>
                )}
              </button>
            </div>
          </div>
        </div>

      </main>
    </div>
  );
}
