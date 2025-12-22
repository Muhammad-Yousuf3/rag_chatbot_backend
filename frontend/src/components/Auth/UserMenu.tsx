/**
 * UserMenu component for displaying user info and preferences.
 *
 * T085 [US4] - Provides user menu with settings.
 */

import React, { useState, useCallback } from 'react';
import { UserResponse } from '../../services/api';

export interface UserMenuProps {
  /**
   * Current user.
   */
  user: UserResponse;

  /**
   * Callback when logout is clicked.
   */
  onLogout: () => void;

  /**
   * Callback when preferences are updated.
   */
  onUpdatePreferences?: (preferences: {
    experience_level?: string;
    preferred_language?: string;
  }) => Promise<void>;

  /**
   * Custom class name.
   */
  className?: string;
}

type ExperienceLevel = 'beginner' | 'intermediate' | 'advanced';

const experienceLevelLabels: Record<ExperienceLevel, string> = {
  beginner: 'Beginner',
  intermediate: 'Intermediate',
  advanced: 'Advanced',
};

/**
 * UserMenu component.
 */
export const UserMenu: React.FC<UserMenuProps> = ({
  user,
  onLogout,
  onUpdatePreferences,
  className = '',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);

  const displayName = user.display_name || user.email.split('@')[0];
  const initials = displayName.slice(0, 2).toUpperCase();

  /**
   * Handle experience level change.
   */
  const handleExperienceLevelChange = useCallback(
    async (level: ExperienceLevel) => {
      if (!onUpdatePreferences || isUpdating) return;

      setIsUpdating(true);
      try {
        await onUpdatePreferences({ experience_level: level });
      } catch (err) {
        console.error('Failed to update preferences:', err);
      } finally {
        setIsUpdating(false);
      }
    },
    [onUpdatePreferences, isUpdating]
  );

  /**
   * Handle language change.
   */
  const handleLanguageChange = useCallback(
    async (language: string) => {
      if (!onUpdatePreferences || isUpdating) return;

      setIsUpdating(true);
      try {
        await onUpdatePreferences({ preferred_language: language });
      } catch (err) {
        console.error('Failed to update preferences:', err);
      } finally {
        setIsUpdating(false);
      }
    },
    [onUpdatePreferences, isUpdating]
  );

  return (
    <div
      className={`user-menu ${className}`}
      style={{ position: 'relative', display: 'inline-block' }}
    >
      {/* Avatar button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 12px',
          backgroundColor: 'transparent',
          border: '1px solid #e0e0e0',
          borderRadius: '20px',
          cursor: 'pointer',
          fontSize: '14px',
        }}
      >
        <div
          style={{
            width: '28px',
            height: '28px',
            borderRadius: '50%',
            backgroundColor: '#1976d2',
            color: '#ffffff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '12px',
            fontWeight: '600',
          }}
        >
          {initials}
        </div>
        <span>{displayName}</span>
        <span style={{ fontSize: '10px' }}>{isOpen ? '▲' : '▼'}</span>
      </button>

      {/* Dropdown menu */}
      {isOpen && (
        <div
          style={{
            position: 'absolute',
            top: '100%',
            right: 0,
            marginTop: '4px',
            backgroundColor: '#ffffff',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            minWidth: '220px',
            zIndex: 1000,
          }}
        >
          {/* User info */}
          <div
            style={{
              padding: '12px 16px',
              borderBottom: '1px solid #e0e0e0',
            }}
          >
            <div style={{ fontWeight: '600', fontSize: '14px' }}>{displayName}</div>
            <div style={{ fontSize: '12px', color: '#666666' }}>{user.email}</div>
            {user.experience_level && (
              <div
                style={{
                  marginTop: '4px',
                  fontSize: '11px',
                  color: '#1976d2',
                  textTransform: 'capitalize',
                }}
              >
                {user.experience_level} level
              </div>
            )}
          </div>

          {/* Menu items */}
          <div style={{ padding: '8px 0' }}>
            <button
              onClick={() => setShowSettings(!showSettings)}
              style={{
                display: 'block',
                width: '100%',
                padding: '8px 16px',
                backgroundColor: 'transparent',
                border: 'none',
                textAlign: 'left',
                cursor: 'pointer',
                fontSize: '14px',
              }}
            >
              Settings {showSettings ? '▼' : '▶'}
            </button>

            {/* Settings panel */}
            {showSettings && (
              <div
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#f5f5f5',
                }}
              >
                {/* Experience level */}
                <div style={{ marginBottom: '12px' }}>
                  <label
                    style={{
                      display: 'block',
                      fontSize: '12px',
                      fontWeight: '500',
                      marginBottom: '4px',
                    }}
                  >
                    Experience Level
                  </label>
                  <select
                    value={user.experience_level || 'beginner'}
                    onChange={(e) =>
                      handleExperienceLevelChange(e.target.value as ExperienceLevel)
                    }
                    disabled={isUpdating}
                    style={{
                      width: '100%',
                      padding: '6px 8px',
                      borderRadius: '4px',
                      border: '1px solid #e0e0e0',
                      fontSize: '13px',
                    }}
                  >
                    {Object.entries(experienceLevelLabels).map(([value, label]) => (
                      <option key={value} value={value}>
                        {label}
                      </option>
                    ))}
                  </select>
                  <div style={{ fontSize: '11px', color: '#666666', marginTop: '4px' }}>
                    Affects how detailed responses are
                  </div>
                </div>

                {/* Language preference */}
                <div>
                  <label
                    style={{
                      display: 'block',
                      fontSize: '12px',
                      fontWeight: '500',
                      marginBottom: '4px',
                    }}
                  >
                    Preferred Language
                  </label>
                  <select
                    value={user.preferred_language || 'en'}
                    onChange={(e) => handleLanguageChange(e.target.value)}
                    disabled={isUpdating}
                    style={{
                      width: '100%',
                      padding: '6px 8px',
                      borderRadius: '4px',
                      border: '1px solid #e0e0e0',
                      fontSize: '13px',
                    }}
                  >
                    <option value="en">English</option>
                    <option value="ur">Urdu</option>
                  </select>
                </div>
              </div>
            )}

            {/* Logout */}
            <button
              onClick={onLogout}
              style={{
                display: 'block',
                width: '100%',
                padding: '8px 16px',
                backgroundColor: 'transparent',
                border: 'none',
                textAlign: 'left',
                cursor: 'pointer',
                fontSize: '14px',
                color: '#c62828',
                marginTop: '4px',
              }}
            >
              Sign Out
            </button>
          </div>
        </div>
      )}

      {/* Click outside to close */}
      {isOpen && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            zIndex: 999,
          }}
          onClick={() => {
            setIsOpen(false);
            setShowSettings(false);
          }}
        />
      )}
    </div>
  );
};

export default UserMenu;
