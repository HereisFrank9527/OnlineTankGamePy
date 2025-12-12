import * as PIXI from 'pixi.js';
import { TankState, Projectile, GameMap } from '../types';

export interface GameControls {
  moveUp: boolean;
  moveDown: boolean;
  moveLeft: boolean;
  moveRight: boolean;
  fire: boolean;
}

export class GameEngine {
  private app: PIXI.Application;
  private gameContainer: PIXI.Container;
  private tankGraphics: Map<number, PIXI.Graphics> = new Map();
  private projectileGraphics: Map<number, PIXI.Graphics> = new Map();
  private gameMap: GameMap | null = null;
  private controls: GameControls = {
    moveUp: false,
    moveDown: false,
    moveLeft: false,
    moveRight: false,
    fire: false,
  };
  private onTankStateChange?: (x: number, y: number, rotation: number, velocityX: number, velocityY: number) => void;
  private onFireProjectile?: (x: number, y: number, rotation: number) => void;
  private lastUpdateTime = 0;
  private playerId: number | null = null;

  constructor(parentElement: HTMLElement) {
    this.app = new PIXI.Application();
    
    this.app.init({
      width: 800,
      height: 600,
      backgroundColor: 0x2c3e50,
      antialias: true,
    }).then(() => {
      parentElement.appendChild(this.app.canvas);
      this.setupGameContainer();
      this.setupKeyboardControls();
      this.app.ticker.add(this.update.bind(this));
    });
  }

  private setupGameContainer(): void {
    this.gameContainer = new PIXI.Container();
    this.app.stage.addChild(this.gameContainer);
  }

  private setupKeyboardControls(): void {
    const handleKeyDown = (event: KeyboardEvent) => {
      switch (event.code) {
        case 'KeyW':
        case 'ArrowUp':
          this.controls.moveUp = true;
          event.preventDefault();
          break;
        case 'KeyS':
        case 'ArrowDown':
          this.controls.moveDown = true;
          event.preventDefault();
          break;
        case 'KeyA':
        case 'ArrowLeft':
          this.controls.moveLeft = true;
          event.preventDefault();
          break;
        case 'KeyD':
        case 'ArrowRight':
          this.controls.moveRight = true;
          event.preventDefault();
          break;
        case 'Space':
          this.controls.fire = true;
          event.preventDefault();
          break;
      }
    };

    const handleKeyUp = (event: KeyboardEvent) => {
      switch (event.code) {
        case 'KeyW':
        case 'ArrowUp':
          this.controls.moveUp = false;
          break;
        case 'KeyS':
        case 'ArrowDown':
          this.controls.moveDown = false;
          break;
        case 'KeyA':
        case 'ArrowLeft':
          this.controls.moveLeft = false;
          break;
        case 'KeyD':
        case 'ArrowRight':
          this.controls.moveRight = false;
          break;
        case 'Space':
          this.controls.fire = false;
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keyup', handleKeyUp);

    // Cleanup function to be called when component unmounts
    this.app.ticker.add(() => {
      // Store cleanup handlers if needed
    });
  }

  private update(deltaTime: number): void {
    const currentTime = Date.now();
    const deltaMs = currentTime - this.lastUpdateTime;
    
    // Update at 60 FPS (approximately every 16ms)
    if (deltaMs < 16) return;
    
    this.lastUpdateTime = currentTime;

    // Handle local player controls
    if (this.playerId) {
      this.handlePlayerControls(deltaTime);
    }

    // Update projectile positions (this would normally be handled by the server)
    this.updateProjectiles(deltaTime);
  }

  private handlePlayerControls(deltaTime: number): void {
    const playerTank = this.getPlayerTank();
    if (!playerTank) return;

    let velocityX = 0;
    let velocityY = 0;
    let rotation = playerTank.rotation;

    const speed = 200; // pixels per second
    const rotationSpeed = 3; // radians per second

    if (this.controls.moveUp) {
      velocityY = -speed;
    }
    if (this.controls.moveDown) {
      velocityY = speed;
    }
    if (this.controls.moveLeft) {
      rotation -= rotationSpeed * deltaTime / 1000;
    }
    if (this.controls.moveRight) {
      rotation += rotationSpeed * deltaTime / 1000;
    }

    // Update position
    playerTank.x += velocityX * deltaTime / 1000;
    playerTank.y += velocityY * deltaTime / 1000;

    // Keep within bounds
    playerTank.x = Math.max(20, Math.min(780, playerTank.x));
    playerTank.y = Math.max(20, Math.min(580, playerTank.y));

    // Fire projectile
    if (this.controls.fire) {
      this.fireProjectile(playerTank);
      this.controls.fire = false; // Single shot per key press
    }

    // Notify parent component of state change
    if (this.onTankStateChange) {
      this.onTankStateChange(
        playerTank.x,
        playerTank.y,
        rotation,
        velocityX,
        velocityY
      );
    }

    this.updateTankGraphics();
  }

  private fireProjectile(tank: TankState): void {
    if (this.onFireProjectile) {
      const projectileX = tank.x + Math.cos(tank.rotation) * 30;
      const projectileY = tank.y + Math.sin(tank.rotation) * 30;
      
      this.onFireProjectile(projectileX, projectileY, tank.rotation);
    }
  }

  private updateProjectiles(deltaTime: number): void {
    this.projectileGraphics.forEach((graphics, id) => {
      // This would normally update projectile positions based on server data
      // For now, we'll just render the current state
    });
  }

  private getPlayerTank(): TankState | null {
    const playerTank = this.tankStates.find(tank => tank.player_id === this.playerId);
    return playerTank || null;
  }

  private tankStates: TankState[] = [];
  private projectiles: Projectile[] = [];

  updateTankStates(tankStates: TankState[]): void {
    this.tankStates = tankStates;
    this.updateTankGraphics();
  }

  updateProjectiles(projectiles: Projectile[]): void {
    this.projectiles = projectiles;
    this.updateProjectileGraphics();
  }

  private updateTankGraphics(): void {
    // Remove tanks that no longer exist
    const currentTankIds = new Set(this.tankStates.map(tank => tank.player_id));
    this.tankGraphics.forEach((graphics, tankId) => {
      if (!currentTankIds.has(tankId)) {
        this.gameContainer.removeChild(graphics);
        this.tankGraphics.delete(tankId);
      }
    });

    // Add/update tank graphics
    this.tankStates.forEach(tank => {
      if (!this.tankGraphics.has(tank.player_id)) {
        const graphics = new PIXI.Graphics();
        this.gameContainer.addChild(graphics);
        this.tankGraphics.set(tank.player_id, graphics);
      }

      const graphics = this.tankGraphics.get(tank.player_id)!;
      graphics.clear();
      
      if (tank.is_alive) {
        // Draw tank
        graphics.fill(0x00ff00); // Green for all tanks (can be different colors per player)
        graphics.fillRect(-15, -10, 30, 20); // Tank body
        
        graphics.fill(0xffffff);
        graphics.fillRect(10, -3, 20, 6); // Tank barrel
        
        graphics.rotation = tank.rotation;
        graphics.position.set(tank.x, tank.y);
      }
    });
  }

  private updateProjectileGraphics(): void {
    // Remove projectiles that no longer exist
    const currentProjectileIds = new Set(this.projectiles.map(p => p.id));
    this.projectileGraphics.forEach((graphics, id) => {
      if (!currentProjectileIds.has(id)) {
        this.gameContainer.removeChild(graphics);
        this.projectileGraphics.delete(id);
      }
    });

    // Add/update projectile graphics
    this.projectiles.forEach(projectile => {
      if (!this.projectileGraphics.has(projectile.id)) {
        const graphics = new PIXI.Graphics();
        this.gameContainer.addChild(graphics);
        this.projectileGraphics.set(projectile.id, graphics);
      }

      const graphics = this.projectileGraphics.get(projectile.id)!;
      graphics.clear();
      
      graphics.fill(0xffff00); // Yellow projectiles
      graphics.fillRect(-2, -2, 4, 4); // Small square projectile
      
      graphics.position.set(projectile.x, projectile.y);
    });
  }

  setGameMap(gameMap: GameMap): void {
    this.gameMap = gameMap;
    this.renderGameMap();
  }

  private renderGameMap(): void {
    if (!this.gameMap) return;

    // Draw obstacles
    this.gameMap.obstacles.forEach((obstacle, index) => {
      const graphics = new PIXI.Graphics();
      graphics.fill(0x8B4513); // Brown obstacles
      graphics.fillRect(obstacle.x, obstacle.y, obstacle.width, obstacle.height);
      this.gameContainer.addChild(graphics);
    });

    // Draw power-ups
    this.gameMap.powerUps.forEach((powerUp, index) => {
      const graphics = new PIXI.Graphics();
      graphics.fill(0xff00ff); // Magenta power-ups
      graphics.fillCircle(powerUp.x, powerUp.y, 10);
      this.gameContainer.addChild(graphics);
    });

    // Draw spawn points (for debugging)
    this.gameMap.spawnPoints.forEach((spawn, index) => {
      const graphics = new PIXI.Graphics();
      graphics.stroke(0x00ffff, 2); // Cyan outline
      graphics.strokeRect(spawn.x - 15, spawn.y - 15, 30, 30);
      this.gameContainer.addChild(graphics);
    });
  }

  setPlayerId(playerId: number): void {
    this.playerId = playerId;
  }

  setOnTankStateChange(callback: (x: number, y: number, rotation: number, velocityX: number, velocityY: number) => void): void {
    this.onTankStateChange = callback;
  }

  setOnFireProjectile(callback: (x: number, y: number, rotation: number) => void): void {
    this.onFireProjectile = callback;
  }

  destroy(): void {
    this.app.destroy(true);
  }

  resize(width: number, height: number): void {
    this.app.renderer.resize(width, height);
  }
}
