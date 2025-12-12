import React, { useState, useEffect } from 'react';
import { useAuthStore, useRoomStore, useUIStore } from '../store';
import { apiService } from '../services/api';
import { wsService } from '../services/websocket';
import { Room, RoomMember } from '../types';
import './LobbyView.css';

const LobbyView: React.FC = () => {
  const [showCreateRoom, setShowCreateRoom] = useState(false);
  const [roomName, setRoomName] = useState('');
  const [joinRoomCode, setJoinRoomCode] = useState('');
  const [isJoining, setIsJoining] = useState(false);
  
  const { user } = useAuthStore();
  const { 
    currentRoom, 
    availableRooms, 
    roomMembers, 
    isLoading, 
    error,
    fetchAvailableRooms,
    createRoom,
    joinRoom,
    leaveRoom,
    setReady,
    startGame,
    setCurrentRoom,
    setRoomMembers
  } = useRoomStore();
  const { showError } = useUIStore();

  useEffect(() => {
    fetchAvailableRooms();
    const interval = setInterval(fetchAvailableRooms, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, [fetchAvailableRooms]);

  useEffect(() => {
    // Set up WebSocket listeners when in a room
    if (currentRoom) {
      const handlePlayerJoined = (data: { player: any }) => {
        console.log('Player joined:', data.player);
        refreshRoomData();
      };

      const handlePlayerLeft = (data: { player_id: number }) => {
        console.log('Player left:', data.player_id);
        refreshRoomData();
      };

      wsService.on('player_joined', handlePlayerJoined);
      wsService.on('player_left', handlePlayerLeft);

      return () => {
        wsService.off('player_joined', handlePlayerJoined);
        wsService.off('player_left', handlePlayerLeft);
      };
    }
  }, [currentRoom]);

  const refreshRoomData = async () => {
    if (currentRoom) {
      try {
        const room = await apiService.getRoom(currentRoom.code);
        setCurrentRoom(room);
        if (room.members) {
          setRoomMembers(room.members);
        }
      } catch (error) {
        console.error('Failed to refresh room data:', error);
      }
    }
  };

  const handleCreateRoom = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!roomName.trim()) return;

    try {
      const room = await createRoom(roomName.trim());
      await connectToRoom(room.code);
      setShowCreateRoom(false);
      setRoomName('');
    } catch (error: any) {
      showError(error.message || 'Failed to create room');
    }
  };

  const handleJoinRoom = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!joinRoomCode.trim()) return;

    setIsJoining(true);
    try {
      const room = await joinRoom(joinRoomCode.trim().toUpperCase());
      await connectToRoom(room.code);
      setJoinRoomCode('');
    } catch (error: any) {
      showError(error.message || 'Failed to join room');
    } finally {
      setIsJoining(false);
    }
  };

  const handleLeaveRoom = async () => {
    try {
      wsService.disconnect();
      await leaveRoom();
    } catch (error: any) {
      showError(error.message || 'Failed to leave room');
    }
  };

  const handleReady = async (isReady: boolean) => {
    try {
      await setReady(isReady);
      refreshRoomData();
    } catch (error: any) {
      showError(error.message || 'Failed to set ready status');
    }
  };

  const handleStartGame = async () => {
    try {
      await startGame();
      // Game will start via WebSocket message
    } catch (error: any) {
      showError(error.message || 'Failed to start game');
    }
  };

  const connectToRoom = async (roomCode: string) => {
    try {
      await wsService.connect(roomCode);
    } catch (error: any) {
      showError('Failed to connect to room');
    }
  };

  const getReadyCount = () => {
    return roomMembers.filter(member => member.is_ready).length;
  };

  const isUserReady = () => {
    return roomMembers.find(member => member.player.id === user?.id)?.is_ready || false;
  };

  const isUserOwner = () => {
    return roomMembers.find(member => member.player.id === user?.id)?.id === roomMembers[0]?.id;
  };

  if (currentRoom) {
    return (
      <div className="lobby-container">
        <div className="room-info">
          <h2>Room: {currentRoom.name}</h2>
          <p>Code: <span className="room-code">{currentRoom.code}</span></p>
          <p>Players: {roomMembers.length}/{currentRoom.max_players}</p>
        </div>

        <div className="room-members">
          <h3>Players ({roomMembers.length}/{currentRoom.max_players})</h3>
          <div className="members-list">
            {roomMembers.map((member) => (
              <div key={member.id} className="member-card">
                <div className="member-info">
                  <span className="member-username">{member.player.username}</span>
                  <span className="member-stats">
                    Kills: {member.player.kills} | Deaths: {member.player.deaths}
                  </span>
                </div>
                <div className={`member-status ${member.is_ready ? 'ready' : 'not-ready'}`}>
                  {member.is_ready ? '✓ Ready' : '✗ Not Ready'}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="room-actions">
          <div className="ready-section">
            <button
              onClick={() => handleReady(!isUserReady())}
              className={`ready-btn ${isUserReady() ? 'ready' : 'not-ready'}`}
              disabled={currentRoom.status !== 'waiting'}
            >
              {isUserReady() ? 'Unready' : 'Ready'}
            </button>
            <span className="ready-count">
              {getReadyCount()}/{roomMembers.length} ready
            </span>
          </div>

          <div className="room-controls">
            {isUserOwner() && (
              <button
                onClick={handleStartGame}
                className="start-game-btn"
                disabled={getReadyCount() < 2 || currentRoom.status !== 'waiting'}
              >
                Start Game
              </button>
            )}
            <button onClick={handleLeaveRoom} className="leave-room-btn">
              Leave Room
            </button>
          </div>
        </div>

        <div className="room-status">
          <p>Status: <span className={`status-${currentRoom.status}`}>{currentRoom.status}</span></p>
          {currentRoom.status === 'waiting' && (
            <p className="waiting-message">
              {getReadyCount() < 2 
                ? 'Need at least 2 players to start' 
                : 'Ready to start!'}
            </p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="lobby-container">
      <div className="lobby-header">
        <h2>Game Lobby</h2>
        <button onClick={() => fetchAvailableRooms()} className="refresh-btn" disabled={isLoading}>
          {isLoading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {error && (
        <div className="lobby-error">
          {error}
        </div>
      )}

      <div className="lobby-actions">
        <button 
          onClick={() => setShowCreateRoom(!showCreateRoom)} 
          className="create-room-btn"
          disabled={isLoading}
        >
          Create New Room
        </button>

        <form onSubmit={handleJoinRoom} className="join-room-form">
          <input
            type="text"
            value={joinRoomCode}
            onChange={(e) => setJoinRoomCode(e.target.value.toUpperCase())}
            placeholder="Enter room code"
            maxLength={6}
            disabled={isJoining}
            required
          />
          <button type="submit" disabled={isJoining || !joinRoomCode.trim()}>
            {isJoining ? 'Joining...' : 'Join Room'}
          </button>
        </form>
      </div>

      {showCreateRoom && (
        <form onSubmit={handleCreateRoom} className="create-room-form">
          <input
            type="text"
            value={roomName}
            onChange={(e) => setRoomName(e.target.value)}
            placeholder="Enter room name"
            disabled={isLoading}
            required
            autoFocus
          />
          <div className="create-room-actions">
            <button type="submit" disabled={isLoading || !roomName.trim()}>
              {isLoading ? 'Creating...' : 'Create Room'}
            </button>
            <button type="button" onClick={() => setShowCreateRoom(false)}>
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="available-rooms">
        <h3>Available Rooms</h3>
        {availableRooms.length === 0 ? (
          <p className="no-rooms">No available rooms. Create one to start playing!</p>
        ) : (
          <div className="rooms-grid">
            {availableRooms.map((room: Room) => (
              <div key={room.id} className="room-card">
                <div className="room-header">
                  <h4>{room.name}</h4>
                  <span className={`room-status status-${room.status}`}>
                    {room.status}
                  </span>
                </div>
                <div className="room-details">
                  <p>Code: <span className="room-code">{room.code}</span></p>
                  <p>Players: {room.members?.length || 0}/{room.max_players}</p>
                  <p>Created: {new Date(room.created_at).toLocaleTimeString()}</p>
                </div>
                <button
                  onClick={() => {
                    joinRoom(room.code).then(() => connectToRoom(room.code));
                  }}
                  className="join-room-btn"
                  disabled={room.status !== 'waiting' || (room.members?.length || 0) >= room.max_players}
                >
                  {room.status !== 'waiting' ? 'Game in Progress' : 
                   (room.members?.length || 0) >= room.max_players ? 'Room Full' : 'Join'}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default LobbyView;
