'use client';

import React from 'react';
import './LeaderboardEntry.css';

interface LeaderboardUser {
  id: string;
  name: string;
  email?: string;
  streak: number;
  checkins?: number;
  events?: number;
}

interface LeaderboardEntryProps {
  user: LeaderboardUser;
  rank: number;
  showDetails?: boolean; // Controls whether to show checkins and events
}

export const LeaderboardEntry: React.FC<LeaderboardEntryProps> = ({ user, rank, showDetails = true }) => {
  // Get user initials for avatar
  const getUserInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase();
  };

  // Determine crown/medal based on rank
  const getRankDisplay = (rank: number) => {
    if (rank === 1) return { icon: '👑', className: 'rank-1' };
    if (rank === 2) return { icon: '🥈', className: 'rank-2' };
    if (rank === 3) return { icon: '🥉', className: 'rank-3' };
    return { icon: rank.toString(), className: '' };
  };

  const { icon, className } = getRankDisplay(rank);

  return (
    <tr key={user.id}>
      <td className="rank-cell">
        {rank <= 3 ? (
          <div className={`top-rank ${className}`}>{icon}</div>
        ) : (
          <div className="numeric-rank">{rank}</div>
        )}
      </td>
      <td>
        <div className="user-cell">
          <div className={`user-avatar ${className}`}>
            {getUserInitials(user.name)}
          </div>
          <div className="user-info">
            <span className="user-name">{user.name}</span>
            {user.email && showDetails && <span className="user-email">{user.email}</span>}
          </div>
        </div>
      </td>
      <td className="streak-cell">{user.streak} days</td>
      {showDetails && user.checkins !== undefined && (
        <td className="checkins-cell">{user.checkins}</td>
      )}
      {showDetails && user.events !== undefined && (
        <td className="events-cell">{user.events}</td>
      )}
    </tr>
  );
};