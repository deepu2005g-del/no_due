/**
 * Layout component - wraps all authenticated pages.
 * Provides sidebar navigation and top navbar with notifications.
 */
import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import API from '../api/axios'
import { HiOutlineHome, HiOutlineBell, HiOutlineLogout, HiOutlineMenu, HiOutlineX,
         HiOutlineClipboardList, HiOutlineUserGroup, HiOutlineShieldCheck, 
         HiOutlineAcademicCap, HiOutlineTicket, HiOutlineChartBar } from 'react-icons/hi'

// Sidebar menu items per role
const menuItems = {
  student: [
    { label: 'Dashboard', icon: HiOutlineHome, path: '/student' },
  ],
  faculty: [
    { label: 'Dashboard', icon: HiOutlineHome, path: '/faculty' },
  ],
  admin: [
    { label: 'Dashboard', icon: HiOutlineHome, path: '/admin' },
  ],
  hod: [
    { label: 'Dashboard', icon: HiOutlineHome, path: '/hod' },
  ],
  staff: [
    { label: 'Dashboard', icon: HiOutlineHome, path: '/staff' },
  ],
}

const roleLabels = {
  student: 'Student',
  faculty: 'Faculty Advisor',
  admin: 'Administrator',
  hod: 'Head of Department',
  staff: 'Department Staff',
}

const roleIcons = {
  student: HiOutlineAcademicCap,
  faculty: HiOutlineUserGroup,
  admin: HiOutlineShieldCheck,
  hod: HiOutlineClipboardList,
  staff: HiOutlineTicket,
}

export default function Layout({ children }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [notifications, setNotifications] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [showNotifs, setShowNotifs] = useState(false)

  // Fetch notifications
  useEffect(() => {
    fetchNotifications()
    const interval = setInterval(fetchNotifications, 30000) // Poll every 30s
    return () => clearInterval(interval)
  }, [])

  const fetchNotifications = async () => {
    try {
      const res = await API.get('/notifications/')
      setNotifications(res.data.notifications || [])
      setUnreadCount(res.data.unread_count || 0)
    } catch (err) {
      // Silently fail - notifications are non-critical
    }
  }

  const markAsRead = async (id) => {
    try {
      await API.put(`/notifications/${id}/read`)
      fetchNotifications()
    } catch (err) {}
  }

  const markAllRead = async () => {
    try {
      await API.put('/notifications/read-all')
      fetchNotifications()
    } catch (err) {}
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const RoleIcon = roleIcons[user?.role] || HiOutlineHome
  const items = menuItems[user?.role] || []

  return (
    <div className="min-h-screen flex bg-surface-950">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <aside className={`fixed lg:static inset-y-0 left-0 z-50 w-72 transform transition-transform duration-300 
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0
        bg-surface-900/95 backdrop-blur-xl border-r border-surface-700/50 flex flex-col`}>
        
        {/* Logo Section */}
        <div className="p-6 border-b border-surface-700/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center shadow-lg shadow-primary-500/30">
              <HiOutlineShieldCheck className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white">No-Due</h1>
              <p className="text-xs text-surface-400">Clearance System</p>
            </div>
          </div>
        </div>

        {/* User Info */}
        <div className="p-4 mx-3 mt-4 rounded-xl bg-surface-800/50 border border-surface-700/30">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-purple-600 flex items-center justify-center text-white font-bold text-sm">
              {user?.name?.charAt(0)?.toUpperCase() || 'U'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-white truncate">{user?.name}</p>
              <p className="text-xs text-primary-400">{roleLabels[user?.role] || user?.role}</p>
            </div>
          </div>
        </div>

        {/* Nav Items */}
        <nav className="flex-1 p-4 space-y-1 mt-2">
          {items.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            return (
              <button
                key={item.path}
                onClick={() => { navigate(item.path); setSidebarOpen(false) }}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200
                  ${isActive 
                    ? 'bg-primary-500/15 text-primary-400 border border-primary-500/20 shadow-lg shadow-primary-500/5' 
                    : 'text-surface-300 hover:bg-surface-700/50 hover:text-white'
                  }`}
              >
                <Icon className="w-5 h-5" />
                {item.label}
              </button>
            )
          })}
        </nav>

        {/* Logout */}
        <div className="p-4 border-t border-surface-700/50">
          <button onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-red-400 hover:bg-red-500/10 transition-all">
            <HiOutlineLogout className="w-5 h-5" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-h-screen">
        {/* Top Navbar */}
        <header className="sticky top-0 z-30 bg-surface-900/80 backdrop-blur-xl border-b border-surface-700/50">
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center gap-4">
              {/* Mobile menu toggle */}
              <button onClick={() => setSidebarOpen(!sidebarOpen)} className="lg:hidden text-surface-300 hover:text-white">
                {sidebarOpen ? <HiOutlineX className="w-6 h-6" /> : <HiOutlineMenu className="w-6 h-6" />}
              </button>
              <div>
                <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                  <RoleIcon className="w-5 h-5 text-primary-400" />
                  {roleLabels[user?.role]} Dashboard
                </h2>
              </div>
            </div>

            {/* Notifications Bell */}
            <div className="relative">
              <button 
                onClick={() => setShowNotifs(!showNotifs)}
                className="relative p-2 rounded-xl text-surface-300 hover:text-white hover:bg-surface-700/50 transition-all"
              >
                <HiOutlineBell className="w-6 h-6" />
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center font-bold animate-pulse">
                    {unreadCount}
                  </span>
                )}
              </button>

              {/* Notifications Dropdown */}
              {showNotifs && (
                <div className="absolute right-0 top-12 w-80 max-h-96 overflow-y-auto glass-card p-2 animate-slide-up z-50">
                  <div className="flex items-center justify-between px-3 py-2 mb-1">
                    <h3 className="text-sm font-semibold text-white">Notifications</h3>
                    {unreadCount > 0 && (
                      <button onClick={markAllRead} className="text-xs text-primary-400 hover:text-primary-300">
                        Mark all read
                      </button>
                    )}
                  </div>
                  {notifications.length === 0 ? (
                    <p className="text-sm text-surface-400 text-center py-4">No notifications</p>
                  ) : (
                    notifications.slice(0, 10).map((n) => (
                      <div
                        key={n.id}
                        onClick={() => markAsRead(n.id)}
                        className={`px-3 py-2.5 rounded-lg cursor-pointer transition-all text-sm mb-1
                          ${n.is_read ? 'text-surface-400' : 'text-white bg-surface-700/50 border-l-2 border-primary-500'}`}
                      >
                        <p className="leading-snug">{n.message}</p>
                        <p className="text-xs text-surface-500 mt-1">
                          {new Date(n.created_at).toLocaleString()}
                        </p>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-6 page-enter">
          {children}
        </main>
      </div>
    </div>
  )
}
