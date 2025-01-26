from moviepy.video.io.VideoFileClip import VideoFileClip


def trim_video(file_path, max_duration=90):
    """
    Vérifie la durée d'une vidéo et la coupe à max_duration secondes si nécessaire.

    Args:
        file_path (str): Chemin vers la vidéo.
        max_duration (int): Durée maximale autorisée en secondes.

    Returns:
        str: Chemin vers la vidéo coupée (ou l'original si aucune coupe n'est nécessaire).
    """
    # Charger la vidéo
    video = VideoFileClip(file_path)
    print(f"Durée de la vidéo : {video.duration:.2f} secondes")

    # Vérifier si la vidéo dépasse la durée maximale
    if video.duration > max_duration:
        output_path = file_path.replace(".mp4", f"_trimmed_{max_duration}s.mp4")
        # Couper la vidéo à max_duration secondes
        trimmed_video = video.subclipped(0, max_duration)  # Remplacement de subclip par subclipped
        trimmed_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
        print(f"Vidéo coupée et enregistrée sous : {output_path}")
        return output_path

    print("La vidéo est déjà dans la durée permise.")
    return file_path


