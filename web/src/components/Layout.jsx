import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const links = [
  { to: '/', icon: '🏠', label: 'Home', end: true },
  { to: '/history', icon: '🕐', label: 'History' },
  { to: '/account', icon: '⚙️', label: 'Account' },
];

// Sidebar on desktop, bottom tab bar on phones
export default function Layout({ children }) {
  const { user, signOut } = useAuth();

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">🎵</div>
          <span className="brand-name">MoodQueue</span>
        </div>
        <nav className="nav">
          {links.map((l) => (
            <NavLink key={l.to} to={l.to} end={l.end}>
              <span>{l.icon}</span> {l.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-user">
          <div className="avatar">{user?.username?.[0]?.toUpperCase()}</div>
          <div className="user-info">
            <div className="user-name">{user?.username}</div>
            <div className="user-email">{user?.email}</div>
          </div>
          <button className="icon-btn" onClick={signOut} title="Sign out" aria-label="Sign out">↪</button>
        </div>
      </aside>

      <main className="main">
        <div className="content">{children}</div>
      </main>

      <nav className="mobile-bar">
        {links.map((l) => (
          <NavLink key={l.to} to={l.to} end={l.end}>
            <span>{l.icon}</span>
            <span>{l.label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
