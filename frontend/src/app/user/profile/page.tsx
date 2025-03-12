'use client';

import { useState, useEffect } from 'react';
import { useAppSelector } from '@/store';
import './styles.css';

export default function ProfilePage() {
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    bio: '',
    phone: '',
  });

  // In a real app, this would come from the Redux store or an API call
  const userProfile = {
    id: '1',
    name: 'John Doe',
    email: 'john.doe@example.com',
    role: 'Teacher',
    bio: 'Mathematics teacher with 5 years of experience.',
    phone: '+1 (555) 123-4567',
    createdAt: '2023-01-15',
    stats: {
      totalAttendance: 145,
      eventsCreated: 24,
      perfectStreak: 15
    },
    achievements: [
      { id: 1, title: 'First Check-in', description: 'Completed your first attendance check-in', icon: '🎯' },
      { id: 2, title: 'Perfect Week', description: 'Perfect attendance for a full week', icon: '🔥' },
      { id: 3, title: 'Event Creator', description: 'Created your first event', icon: '🏆' },
      { id: 4, title: 'Early Bird', description: 'Checked in early 5 times in a row', icon: '🌅' },
    ]
  };

  useEffect(() => {
    // Initialize form data with user profile
    setFormData({
      name: userProfile.name,
      email: userProfile.email,
      bio: userProfile.bio || '',
      phone: userProfile.phone || '',
    });
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // In a real app, dispatch an action to update the profile
    console.log('Profile update submitted:', formData);
    setIsEditing(false);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    }).format(date);
  };

  return (
    <div className="profile-container">
      <div className="profile-content">
        {/* Profile Header */}
        <div className="profile-header">
          <div className="profile-avatar">
            {/* In a real app, this would be an actual image */}
            <svg className="profile-avatar-placeholder w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
            </svg>
          </div>
          <div className="profile-info">
            <h1 className="profile-name">{userProfile.name}</h1>
            <p className="profile-email">{userProfile.email}</p>
            <span className="profile-role">{userProfile.role}</span>
            <p className="mt-2 text-sm text-gray-500">
              Member since {formatDate(userProfile.createdAt)}
            </p>
          </div>
        </div>

        {/* Profile Stats */}
        <div className="profile-section">
          <h2 className="profile-section-title">Attendance Statistics</h2>
          <div className="profile-stats">
            <div className="stat-card">
              <div className="stat-value">{userProfile.stats.totalAttendance}</div>
              <div className="stat-label">Total Check-ins</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{userProfile.stats.eventsCreated}</div>
              <div className="stat-label">Events Created</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{userProfile.stats.perfectStreak}</div>
              <div className="stat-label">Perfect Streak</div>
            </div>
          </div>
        </div>

        {/* Achievements */}
        <div className="profile-section">
          <h2 className="profile-section-title">Achievements</h2>
          <div className="achievements-grid">
            {userProfile.achievements.map(achievement => (
              <div key={achievement.id} className="achievement-card">
                <div className="achievement-icon">
                  <span className="text-xl">{achievement.icon}</span>
                </div>
                <div className="achievement-title">{achievement.title}</div>
                <div className="achievement-desc">{achievement.description}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Profile Information */}
        <div className="profile-section">
          <h2 className="profile-section-title">Profile Information</h2>
          {isEditing ? (
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Name</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  className="form-input"
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Email</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="form-input"
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Bio</label>
                <textarea
                  name="bio"
                  value={formData.bio}
                  onChange={handleInputChange}
                  className="form-input"
                  rows={3}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Phone</label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  className="form-input"
                />
              </div>
              <div className="form-actions">
                <button
                  type="button"
                  className="btn-cancel"
                  onClick={() => setIsEditing(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="btn-save">
                  Save Changes
                </button>
              </div>
            </form>
          ) : (
            <div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-gray-500">Full Name</p>
                  <p className="mt-1">{userProfile.name}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Email</p>
                  <p className="mt-1">{userProfile.email}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Bio</p>
                  <p className="mt-1">{userProfile.bio || 'No bio provided'}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Phone</p>
                  <p className="mt-1">{userProfile.phone || 'No phone provided'}</p>
                </div>
              </div>
              <div className="mt-4">
                <button
                  onClick={() => setIsEditing(true)}
                  className="btn-save"
                >
                  Edit Profile
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}