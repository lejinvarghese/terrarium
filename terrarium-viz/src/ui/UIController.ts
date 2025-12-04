import { TerrariumScene } from '../core/TerrariumScene';
import { ServiceStatus, ActivityEvent } from '../systems/StatusMonitor';

export class UIController {
  private scene: TerrariumScene;
  private botsVisible: boolean = true;
  private servicesVisible: boolean = true;
  private particlesVisible: boolean = true;

  constructor(scene: TerrariumScene) {
    this.scene = scene;
    this.setupEventListeners();
  }

  private setupEventListeners() {
    // Toggle bots
    const toggleBotsBtn = document.getElementById('toggle-bots');
    toggleBotsBtn?.addEventListener('click', () => {
      this.botsVisible = !this.botsVisible;
      this.scene.toggleBots(this.botsVisible);
      toggleBotsBtn.textContent = this.botsVisible ? '🤖 Hide Bots' : '🤖 Show Bots';
    });

    // Toggle services
    const toggleServicesBtn = document.getElementById('toggle-services');
    toggleServicesBtn?.addEventListener('click', () => {
      this.servicesVisible = !this.servicesVisible;
      this.scene.toggleServices(this.servicesVisible);
      toggleServicesBtn.textContent = this.servicesVisible ? '⚙️ Hide Services' : '⚙️ Show Services';
    });

    // Toggle particles
    const toggleParticlesBtn = document.getElementById('toggle-particles');
    toggleParticlesBtn?.addEventListener('click', () => {
      this.particlesVisible = !this.particlesVisible;
      this.scene.toggleParticles(this.particlesVisible);
      toggleParticlesBtn.textContent = this.particlesVisible ? '✨ Hide Particles' : '✨ Show Particles';
    });

    // Reset camera
    const resetCameraBtn = document.getElementById('reset-camera');
    resetCameraBtn?.addEventListener('click', () => {
      this.scene.resetCamera();
    });
  }

  public updateStatusPanel(statuses: ServiceStatus[]) {
    const statusList = document.getElementById('status-list');
    if (!statusList) return;

    statusList.innerHTML = statuses.map(status => {
      const statusClass = status.active ? 'status-active' : 'status-inactive';
      const icon = status.type === 'bot' ? '🤖' : '⚙️';

      return `
        <div class="status-item">
          <div style="display: flex; align-items: center;">
            <div class="status-indicator ${statusClass}"></div>
            <span>${icon} ${status.name}</span>
          </div>
          <span style="font-size: 11px; color: rgba(255,255,255,0.5);">
            ${status.active ? 'Active' : 'Inactive'}
          </span>
        </div>
      `;
    }).join('');
  }

  public updateActivityFeed(activities: ActivityEvent[]) {
    const activityList = document.getElementById('activity-list');
    if (!activityList) return;

    // Show only last 10 activities
    const recentActivities = activities.slice(0, 10);

    activityList.innerHTML = recentActivities.map(activity => {
      const typeColors = {
        info: '#00d4ff',
        success: '#00ff88',
        warning: '#ffaa00',
        error: '#ff4444'
      };

      const color = typeColors[activity.type];
      const time = this.formatTime(activity.timestamp);

      return `
        <div class="activity-item" style="border-left-color: ${color};">
          <div style="font-weight: 500; margin-bottom: 4px;">
            ${activity.entity}
          </div>
          <div style="font-size: 12px; color: rgba(255,255,255,0.8);">
            ${activity.message}
          </div>
          <div class="time">${time}</div>
        </div>
      `;
    }).join('');
  }

  private formatTime(date: Date): string {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);

    if (seconds < 60) return `${seconds}s ago`;
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return date.toLocaleDateString();
  }
}
