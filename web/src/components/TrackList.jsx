// Track list with listening links. Works with or without Spotify:
// every track has search links for Spotify, YouTube and Deezer.
export default function TrackList({ tracks }) {
  if (!tracks?.length) return null;
  return (
    <ol className="tracks">
      {tracks.map((t, i) => (
        <li className="track" key={`${t.title}-${t.artist}-${i}`}>
          <span className="track-num">{i + 1}</span>
          <div className="track-meta">
            <div className="track-title">{t.title}</div>
            <div className="track-artist">{t.artist}</div>
          </div>
          <div className="track-links">
            {t.spotify_url && (
              <a className="sp" href={t.spotify_url} target="_blank" rel="noreferrer" title="Spotify">Spotify</a>
            )}
            {t.youtube_url && (
              <a className="yt" href={t.youtube_url} target="_blank" rel="noreferrer" title="YouTube">YouTube</a>
            )}
            {t.deezer_url && (
              <a className="dz" href={t.deezer_url} target="_blank" rel="noreferrer" title="Deezer">Deezer</a>
            )}
          </div>
        </li>
      ))}
    </ol>
  );
}
