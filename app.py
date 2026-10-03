import streamlit as st
import subprocess
import yt_dlp

st.set_page_config(page_title="YouTube Live Restreamer", page_icon="📡", layout="centered")

st.title("📡 YouTube-to-YouTube Live Restreamer")
st.write("Aplikasi *restreaming* otomatis menggunakan link video YouTube, Streamlit, dan FFmpeg.")

stream_key = st.text_input("Masukkan YouTube Stream Key Anda", type="password")
video_url = st.text_input("Masukkan Link Video YouTube (Sumber)", placeholder="https://www.youtube.com/watch?v=xxxxxx")

is_loop = st.checkbox("Putar video secara terus-menerus (Loop)", value=True)

if "process" not in st.session_state:
    st.session_state.process = None

def get_direct_video_url(youtube_url):
    ydl_opts = {'format': 'best[ext=mp4]/best'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info['url']

col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 Mulai Restream", use_container_width=True) and stream_key and video_url:
        if st.session_state.process is None:
            try:
                with st.spinner("Mengambil tautan langsung video sumber..."):
                    direct_url = get_direct_video_url(video_url)
                
                rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"
                
                cmd = ["ffmpeg"]
                if is_loop:
                    cmd.extend(["-stream_loop", "-1"])
                
                cmd.extend([
                    "-re", "-i", direct_url,
                    "-c:v", "libx264", "-preset", "veryfast", "-maxrate", "3000k",
                    "-bufsize", "6000k", "-pix_fmt", "yuv420p", "-g", "50",
                    "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
                    "-f", "flv", rtmp_url
                ])
                
                st.session_state.process = subprocess.Popen(cmd)
                st.success("Proses *streaming* ulang berhasil dimulai!")
                st.rerun()
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
        else:
            st.warning("Streaming sudah berjalan!")

with col2:
    if st.button("⏹️ Stop Restream", use_container_width=True):
        if st.session_state.process is not None:
            st.session_state.process.terminate()
            st.session_state.process.wait()
            st.session_state.process = None
            st.success("Streaming berhasil dihentikan.")
            st.rerun()
        else:
            st.warning("Tidak ada streaming yang sedang berjalan.")

st.divider()
st.subheader("Status Sistem")
if st.session_state.process is not None:
    st.markdown("🔴 **Status:** `LIVE (Sedang Berjalan)`")
else:
    st.markdown("⚪ **Status:** `Berhenti (Standby)`")
