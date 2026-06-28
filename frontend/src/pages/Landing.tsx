import { Link, Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { ArrowRight, Sparkles, Video } from "lucide-react";

export default function Landing() {
  const { user, loading } = useAuth();

  if (!loading && user) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 selection:bg-purple-500/30 overflow-hidden relative">
      {/* Background gradients */}
      <div className="absolute top-0 -left-4 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob" />
      <div className="absolute top-0 -right-4 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000" />
      <div className="absolute -bottom-8 left-20 w-72 h-72 bg-indigo-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000" />

      <main className="relative z-10 flex flex-col items-center justify-center min-h-screen max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center pt-20 pb-32">
        
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-slate-900/50 border border-slate-800 text-sm font-medium text-slate-300 mb-8 backdrop-blur-sm">
          <Sparkles className="w-4 h-4 text-purple-400" />
          <span>The AI Copilot for Creators</span>
        </div>

        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-8 bg-clip-text text-transparent bg-gradient-to-br from-white to-slate-400">
          Turn Instagram Reels into <br className="hidden md:block" />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400">Viral LinkedIn Posts</span>
        </h1>
        
        <p className="max-w-2xl text-lg md:text-xl text-slate-400 mb-12">
          PostMorph AI listens to your Reels, transcribes the audio, and uses Llama 3 to write engaging, highly-converting LinkedIn content on complete autopilot.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 items-center justify-center w-full max-w-md mx-auto">
          <Link
            to="/login"
            className="group relative inline-flex items-center justify-center w-full sm:w-auto px-8 py-4 text-base font-semibold text-white transition-all duration-200 bg-purple-600 border border-transparent rounded-xl hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-600 focus:ring-offset-slate-900 overflow-hidden"
          >
            <div className="absolute inset-0 bg-white/20 group-hover:translate-x-full transition-transform duration-500 ease-out -skew-x-12 -ml-4 w-8" />
            <span>Get Started for Free</span>
            <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>

        {/* Feature visualization */}
        <div className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-8 items-center max-w-4xl mx-auto opacity-70">
          <div className="flex flex-col items-center p-6 bg-slate-900/40 rounded-2xl border border-slate-800 backdrop-blur-sm">
            <Video className="w-10 h-10 text-pink-500 mb-4" />
            <h3 className="font-semibold text-lg mb-2">1. Connect Instagram</h3>
            <p className="text-sm text-slate-400 text-center">We automatically fetch your latest published Reel.</p>
          </div>
          <div className="flex justify-center hidden md:flex text-slate-600">
            <ArrowRight className="w-8 h-8" />
          </div>
          <div className="flex flex-col items-center p-6 bg-slate-900/40 rounded-2xl border border-slate-800 backdrop-blur-sm">
            <svg className="w-10 h-10 text-blue-500 mb-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
            </svg>
            <h3 className="font-semibold text-lg mb-2">2. Publish to LinkedIn</h3>
            <p className="text-sm text-slate-400 text-center">AI rewrites the transcript and posts it natively.</p>
          </div>
        </div>

      </main>
    </div>
  );
}
