from transformers import pipeline, set_seed
from gtts import gTTS
import os
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip
from moviepy.video.tools.subtitles import SubtitlesClip
import random

def generate_narrative(prompt, seed):
    # Set up the GPT-2 pipeline
    generator = pipeline('text-generation', model='gpt2')
    set_seed(seed)

    # Generate text
    generated = generator(prompt, max_length=150, num_return_sequences=1)
    return generated[0]['generated_text']

def text_to_audio(text, filename='narrative.mp3'):
    tts = gTTS(text)
    tts.save(filename)
    return filename

def generate_subtitles(narrative, duration):
    words = narrative.split()
    subtitles = []
    start_time = 0
    end_time = 0
    words_per_sec = len(words) / duration  # Calculate average words per second

    for word in words:
        end_time += 1 / words_per_sec  # Increment end time based on average words per second
        subtitles.append(((start_time, end_time), word))
        start_time = end_time

    return subtitles

def create_subtitle_clip(subtitles, video_clip):
    # Function to generate text clips
    def generator(txt):
        return TextClip(txt, font='Arial', fontsize=24, color='white')
    
    # Generate the subtitles clip
    subtitles_clip = SubtitlesClip(subtitles, generator)
    
    # Set the position and duration of the subtitles
    subtitles_clip = subtitles_clip.set_position(('center', 'bottom')).set_duration(video_clip.duration)
    
    return subtitles_clip

def overlay_audio_subtitles_on_video(video_path, audio_path, subtitles, output_path='output_video.mp4'):
    # Load video and audio
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)
    
    # Set audio duration to match video duration if necessary
    if audio_clip.duration > video_clip.duration:
        audio_clip = audio_clip.subclip(0, video_clip.duration)
    
    # Set the audio of the video clip
    video_clip = video_clip.set_audio(audio_clip)
    
    # Create subtitles clip
    subtitles_clip = create_subtitle_clip(subtitles, video_clip)

    # Composite video and subtitles
    final_clip = CompositeVideoClip([video_clip, subtitles_clip])
    
    # Write the result to a file
    final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

def process_videos_in_directory(directory_path, prompt):
    # Get all video files in the directory
    video_files = [f for f in os.listdir(directory_path) if f.endswith(('.mp4', '.mov', '.avi'))]

    # Process each video file
    for index, video_file in enumerate(video_files):
        video_path = os.path.join(directory_path, video_file)
        output_path = os.path.join(directory_path, f"output_{index}_{video_file}")
        
        # Generate a unique narrative for each video using a different seed
        seed = random.randint(0, 10000)
        narrative = generate_narrative(prompt, seed)
        print(f"\nGenerated Narrative for {video_file}:\n")
        print(narrative)
        
        # Convert narrative to audio
        audio_file = text_to_audio(narrative, f'narrative_{index}.mp3')
        print(f"\nAudio file saved as {audio_file}")
        
        # Generate subtitles
        video_clip = VideoFileClip(video_path)
        subtitles = generate_subtitles(narrative, video_clip.duration)
        
        overlay_audio_subtitles_on_video(video_path, audio_file, subtitles, output_path)
        print(f"\nOutput video saved as {output_path}")

def main():
    user_prompt = input("Enter a prompt for the narrative: ")
    directory_path = input("Enter the path to the directory containing video files: ")
    
    process_videos_in_directory(directory_path, user_prompt)

if __name__ == "__main__":
    main()
