import React, { useState } from 'react';
import axios from 'axios';
import { toast } from 'react-hot-toast';
import { motion } from 'framer-motion';

const VideoDownloader = () => {
  const [videoUrl, setVideoUrl] = useState('');
  const [playlistUrl, setPlaylistUrl] = useState('');
  const [outputPath, setOutputPath] = useState('');
  const [downloadStatus, setDownloadStatus] = useState(null);
  const [loading, setLoading] = useState({
    video: false,
    playlist: false
  });

  const [downloadOptions, setDownloadOptions] = useState({
    format: 'video',
    quality: 'highest',
    file_format: 'mp4',
    audio_only: false,
    caption_language: '',
    include_captions: false,
    start_time: '',
    end_time: '',
    compress: false,
    compression_quality: 'medium',
    download_thumbnail: false,
    thumbnail_size: 'maxres',
    extract_chapters: false,
    auto_captions: false,
    convert_format: '',
    conversion_options: {
      video_codec: null,
      audio_codec: null,
      video_bitrate: null,
      audio_bitrate: null,
      preset: 'medium',
      crf: 23
    }
  });

  const [scheduleOptions, setScheduleOptions] = useState({
    enabled: false,
    time: ''
  });

  const handleVideoDownload = async () => {
    if (!videoUrl.trim()) {
      toast.error('Veuillez entrer une URL de vidéo');
      return;
    }

    setLoading(prev => ({ ...prev, video: true }));
    try {
      let result;
      
      if (scheduleOptions.enabled) {
        // Téléchargement programmé
        result = await axios.post('/api/youtube/schedule', {
          video_url: videoUrl,
          schedule_time: scheduleOptions.time,
          output_path: outputPath || undefined,
          options: downloadOptions
        });
        
        if (result.data.success) {
          toast.success(`Téléchargement programmé pour ${scheduleOptions.time}`);
        } else {
          toast.error(`Erreur: ${result.data.error}`);
        }
      } else {
        // Téléchargement immédiat
        result = await axios.post('/api/youtube/download/video', {
          video_url: videoUrl,
          output_path: outputPath || undefined,
          options: downloadOptions
        });
        
        if (result.data.success) {
          toast.success('Vidéo téléchargée avec succès !');
          setDownloadStatus({
            type: 'video',
            ...result.data
          });
        } else {
          toast.error(`Erreur: ${result.data.error}`);
        }
      }
    } catch (error) {
      console.error('Erreur:', error);
      toast.error('Erreur lors du téléchargement');
    } finally {
      setLoading(prev => ({ ...prev, video: false }));
    }
  };

  const handlePlaylistDownload = async () => {
    if (!playlistUrl.trim()) {
      toast.error('Veuillez entrer une URL de playlist');
      return;
    }

    setLoading(prev => ({ ...prev, playlist: true }));
    try {
      const response = await axios.post('/api/youtube/download/playlist', {
        playlist_url: playlistUrl,
        output_path: outputPath || undefined,
        options: downloadOptions
      });

      if (response.data.success) {
        toast.success('Playlist téléchargée avec succès !');
        setDownloadStatus({
          type: 'playlist',
          ...response.data
        });
      } else {
        toast.error(`Erreur: ${response.data.error}`);
      }
    } catch (error) {
      console.error('Erreur:', error);
      toast.error('Erreur lors du téléchargement');
    } finally {
      setLoading(prev => ({ ...prev, playlist: false }));
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDuration = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-semibold mb-6">Téléchargement de vidéos</h3>

      {/* Chemin de sortie */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Dossier de destination (optionnel)
        </label>
        <input
          type="text"
          value={outputPath}
          onChange={(e) => setOutputPath(e.target.value)}
          placeholder="Chemin du dossier de téléchargement"
          className="w-full p-2 border rounded-md"
        />
      </div>

      {/* Options de téléchargement */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <h4 className="font-medium mb-3">Options de téléchargement</h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Format */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Format
            </label>
            <select
              value={downloadOptions.format}
              onChange={(e) => setDownloadOptions(prev => ({
                ...prev,
                format: e.target.value,
                audio_only: e.target.value === 'audio'
              }))}
              className="w-full p-2 border rounded-md"
            >
              <option value="video">Vidéo</option>
              <option value="audio">Audio uniquement</option>
            </select>
          </div>

          {/* Qualité vidéo */}
          {downloadOptions.format === 'video' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Qualité
              </label>
              <select
                value={downloadOptions.quality}
                onChange={(e) => setDownloadOptions(prev => ({
                  ...prev,
                  quality: e.target.value
                }))}
                className="w-full p-2 border rounded-md"
              >
                <option value="highest">Meilleure qualité</option>
                <option value="lowest">Qualité minimale</option>
                <option value="1080p">1080p</option>
                <option value="720p">720p</option>
                <option value="480p">480p</option>
                <option value="360p">360p</option>
              </select>
            </div>
          )}

          {/* Format de fichier */}
          {downloadOptions.format === 'video' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Format de fichier
              </label>
              <select
                value={downloadOptions.file_format}
                onChange={(e) => setDownloadOptions(prev => ({
                  ...prev,
                  file_format: e.target.value
                }))}
                className="w-full p-2 border rounded-md"
              >
                <option value="mp4">MP4</option>
                <option value="webm">WebM</option>
              </select>
            </div>
          )}

          {/* Sous-titres */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Sous-titres
            </label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={downloadOptions.include_captions}
                  onChange={(e) => setDownloadOptions(prev => ({
                    ...prev,
                    include_captions: e.target.checked
                  }))}
                  className="mr-2"
                />
                Inclure les sous-titres
              </label>
              
              {downloadOptions.include_captions && (
                <input
                  type="text"
                  value={downloadOptions.caption_language}
                  onChange={(e) => setDownloadOptions(prev => ({
                    ...prev,
                    caption_language: e.target.value
                  }))}
                  placeholder="Code langue (ex: fr, en) ou vide pour tous"
                  className="w-full p-2 border rounded-md"
                />
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Options avancées */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <h4 className="font-medium mb-3">Options avancées</h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Extraction de segment */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Extraction de segment
            </label>
            <div className="space-y-2">
              <input
                type="text"
                value={downloadOptions.start_time}
                onChange={(e) => setDownloadOptions(prev => ({
                  ...prev,
                  start_time: e.target.value ? parseInt(e.target.value) : ''
                }))}
                placeholder="Temps de début (secondes)"
                className="w-full p-2 border rounded-md"
              />
              <input
                type="text"
                value={downloadOptions.end_time}
                onChange={(e) => setDownloadOptions(prev => ({
                  ...prev,
                  end_time: e.target.value ? parseInt(e.target.value) : ''
                }))}
                placeholder="Temps de fin (secondes)"
                className="w-full p-2 border rounded-md"
              />
            </div>
          </div>

          {/* Compression */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Compression
            </label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={downloadOptions.compress}
                  onChange={(e) => setDownloadOptions(prev => ({
                    ...prev,
                    compress: e.target.checked
                  }))}
                  className="mr-2"
                />
                Activer la compression
              </label>
              
              {downloadOptions.compress && (
                <select
                  value={downloadOptions.compression_quality}
                  onChange={(e) => setDownloadOptions(prev => ({
                    ...prev,
                    compression_quality: e.target.value
                  }))}
                  className="w-full p-2 border rounded-md"
                >
                  <option value="high">Haute qualité</option>
                  <option value="medium">Qualité moyenne</option>
                  <option value="low">Basse qualité</option>
                </select>
              )}
            </div>
          </div>

          {/* Miniature */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Miniature
            </label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={downloadOptions.download_thumbnail}
                  onChange={(e) => setDownloadOptions(prev => ({
                    ...prev,
                    download_thumbnail: e.target.checked
                  }))}
                  className="mr-2"
                />
                Télécharger la miniature
              </label>
              
              {downloadOptions.download_thumbnail && (
                <select
                  value={downloadOptions.thumbnail_size}
                  onChange={(e) => setDownloadOptions(prev => ({
                    ...prev,
                    thumbnail_size: e.target.value
                  }))}
                  className="w-full p-2 border rounded-md"
                >
                  <option value="maxres">Qualité maximale</option>
                  <option value="standard">Standard</option>
                  <option value="high">Haute</option>
                  <option value="medium">Moyenne</option>
                  <option value="default">Par défaut</option>
                </select>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Options avancées supplémentaires */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <h4 className="font-medium mb-3">Options supplémentaires</h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Chapitres et sous-titres */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Chapitres et sous-titres
            </label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={downloadOptions.extract_chapters}
                  onChange={(e) => setDownloadOptions(prev => ({
                    ...prev,
                    extract_chapters: e.target.checked
                  }))}
                  className="mr-2"
                />
                Extraire les chapitres
              </label>
              
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={downloadOptions.auto_captions}
                  onChange={(e) => setDownloadOptions(prev => ({
                    ...prev,
                    auto_captions: e.target.checked
                  }))}
                  className="mr-2"
                />
                Extraire les sous-titres automatiques
              </label>
            </div>
          </div>

          {/* Conversion de format */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Conversion de format
            </label>
            <div className="space-y-2">
              <select
                value={downloadOptions.convert_format}
                onChange={(e) => setDownloadOptions(prev => ({
                  ...prev,
                  convert_format: e.target.value
                }))}
                className="w-full p-2 border rounded-md"
              >
                <option value="">Pas de conversion</option>
                <option value="avi">AVI</option>
                <option value="mkv">MKV</option>
                <option value="mov">MOV</option>
                <option value="wmv">WMV</option>
              </select>
              
              {downloadOptions.convert_format && (
                <div className="space-y-2 mt-2">
                  <select
                    value={downloadOptions.conversion_options.preset}
                    onChange={(e) => setDownloadOptions(prev => ({
                      ...prev,
                      conversion_options: {
                        ...prev.conversion_options,
                        preset: e.target.value
                      }
                    }))}
                    className="w-full p-2 border rounded-md"
                  >
                    <option value="ultrafast">Ultra rapide (qualité minimale)</option>
                    <option value="superfast">Super rapide</option>
                    <option value="veryfast">Très rapide</option>
                    <option value="faster">Plus rapide</option>
                    <option value="fast">Rapide</option>
                    <option value="medium">Moyen (recommandé)</option>
                    <option value="slow">Lent</option>
                    <option value="slower">Plus lent</option>
                    <option value="veryslow">Très lent (meilleure qualité)</option>
                  </select>
                  
                  <input
                    type="number"
                    min="0"
                    max="51"
                    value={downloadOptions.conversion_options.crf}
                    onChange={(e) => setDownloadOptions(prev => ({
                      ...prev,
                      conversion_options: {
                        ...prev.conversion_options,
                        crf: parseInt(e.target.value)
                      }
                    }))}
                    placeholder="Qualité (0-51, plus bas = meilleur)"
                    className="w-full p-2 border rounded-md"
                  />
                </div>
              )}
            </div>
          </div>

          {/* Téléchargement programmé */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Téléchargement programmé
            </label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={scheduleOptions.enabled}
                  onChange={(e) => setScheduleOptions(prev => ({
                    ...prev,
                    enabled: e.target.checked
                  }))}
                  className="mr-2"
                />
                Programmer le téléchargement
              </label>
              
              {scheduleOptions.enabled && (
                <input
                  type="time"
                  value={scheduleOptions.time}
                  onChange={(e) => setScheduleOptions(prev => ({
                    ...prev,
                    time: e.target.value
                  }))}
                  className="w-full p-2 border rounded-md"
                />
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Téléchargement de vidéo unique */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <h4 className="font-medium mb-3">Télécharger une vidéo</h4>
        <div className="flex gap-4">
          <input
            type="text"
            value={videoUrl}
            onChange={(e) => setVideoUrl(e.target.value)}
            placeholder="URL de la vidéo YouTube"
            className="flex-1 p-2 border rounded-md"
          />
          <button
            onClick={handleVideoDownload}
            disabled={loading.video}
            className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 disabled:bg-gray-400"
          >
            {loading.video ? 'Téléchargement...' : 'Télécharger'}
          </button>
        </div>
      </div>

      {/* Téléchargement de playlist */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <h4 className="font-medium mb-3">Télécharger une playlist</h4>
        <div className="flex gap-4">
          <input
            type="text"
            value={playlistUrl}
            onChange={(e) => setPlaylistUrl(e.target.value)}
            placeholder="URL de la playlist YouTube"
            className="flex-1 p-2 border rounded-md"
          />
          <button
            onClick={handlePlaylistDownload}
            disabled={loading.playlist}
            className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 disabled:bg-gray-400"
          >
            {loading.playlist ? 'Téléchargement...' : 'Télécharger la playlist'}
          </button>
        </div>
      </div>

      {/* Affichage du statut */}
      {downloadStatus && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 p-4 bg-green-50 rounded-lg"
        >
          <h4 className="font-medium mb-3">Téléchargement terminé</h4>
          
          {downloadStatus.type === 'video' ? (
            <div className="space-y-2">
              <p><span className="font-medium">Titre:</span> {downloadStatus.title}</p>
              <p><span className="font-medium">Auteur:</span> {downloadStatus.author}</p>
              <p><span className="font-medium">Durée:</span> {formatDuration(downloadStatus.length)}</p>
              <p><span className="font-medium">Vues:</span> {downloadStatus.views.toLocaleString()}</p>
              <p><span className="font-medium">Taille du fichier:</span> {formatFileSize(downloadStatus.file_size)}</p>
              <p><span className="font-medium">Chemin:</span> {downloadStatus.file_path}</p>
              
              {downloadStatus.segment && (
                <p><span className="font-medium">Segment:</span> {downloadStatus.segment.start}s à {downloadStatus.segment.end}s</p>
              )}
              
              {downloadStatus.compressed && (
                <p><span className="font-medium">Compression:</span> {downloadStatus.compression_quality}</p>
              )}
              
              {downloadStatus.thumbnail_path && (
                <div>
                  <p><span className="font-medium">Miniature:</span></p>
                  <img 
                    src={`file://${downloadStatus.thumbnail_path}`} 
                    alt="Miniature"
                    className="mt-2 max-w-xs rounded-lg shadow-sm" 
                  />
                </div>
              )}
              
              {Object.keys(downloadStatus.captions).length > 0 && (
                <div>
                  <p className="font-medium">Sous-titres téléchargés:</p>
                  <ul className="list-disc pl-5 mt-1">
                    {Object.entries(downloadStatus.captions).map(([lang, path]) => (
                      <li key={lang} className="text-sm">
                        {lang}: {path}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-2">
              <p><span className="font-medium">Titre de la playlist:</span> {downloadStatus.playlist_title}</p>
              <p><span className="font-medium">Vidéos totales:</span> {downloadStatus.total_videos}</p>
              <p><span className="font-medium">Vidéos téléchargées:</span> {downloadStatus.downloaded_videos.length}</p>
              <p><span className="font-medium">Échecs:</span> {downloadStatus.failed_videos.length}</p>
              <p><span className="font-medium">Dossier:</span> {downloadStatus.output_path}</p>
              
              {downloadStatus.failed_videos.length > 0 && (
                <div className="mt-4">
                  <p className="font-medium text-red-600">Vidéos non téléchargées:</p>
                  <ul className="list-disc pl-5 mt-2">
                    {downloadStatus.failed_videos.map((video, index) => (
                      <li key={index} className="text-sm text-red-600">
                        {video.url} - {video.error}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
};

export default VideoDownloader;
