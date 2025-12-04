import { TerrariumScene } from '../core/TerrariumScene';
import { UIController } from '../ui/UIController';

export interface ServiceStatus {
  name: string;
  active: boolean;
  type: 'bot' | 'service';
}

export interface ActivityEvent {
  timestamp: Date;
  entity: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
}

export class StatusMonitor {
  private scene: TerrariumScene;
  private ui: UIController;
  private updateInterval: number = 5000; // 5 seconds
  private activities: ActivityEvent[] = [];

  constructor(scene: TerrariumScene, ui: UIController) {
    this.scene = scene;
    this.ui = ui;

    // Start monitoring
    this.startMonitoring();

    // Simulate some initial activity
    this.simulateInitialActivity();
  }

  private startMonitoring() {
    // Check system status periodically
    setInterval(() => {
      this.checkSystemStatus();
    }, this.updateInterval);

    // Initial check
    this.checkSystemStatus();
  }

  private async checkSystemStatus() {
    try {
      // In a real implementation, this would fetch from your backend
      // For now, we'll simulate status checks
      const statuses = await this.fetchSystemStatus();

      statuses.forEach(status => {
        if (status.type === 'bot') {
          this.scene.updateBotStatus(status.name, status.active);
        } else if (status.type === 'service') {
          this.scene.updateServiceStatus(status.name, status.active);
        }
      });

      this.ui.updateStatusPanel(statuses);
    } catch (error) {
      console.error('Failed to fetch system status:', error);
    }
  }

  private async fetchSystemStatus(): Promise<ServiceStatus[]> {
    // Simulate fetching status from backend
    // In production, this would call your status monitoring API
    return new Promise((resolve) => {
      setTimeout(() => {
        const statuses: ServiceStatus[] = [
          // Services
          { name: 'Dome', active: Math.random() > 0.2, type: 'service' },
          { name: 'Engine', active: Math.random() > 0.3, type: 'service' },
          { name: 'Portal', active: Math.random() > 0.3, type: 'service' },
          { name: 'Bridge', active: Math.random() > 0.4, type: 'service' },
          { name: 'Archive', active: Math.random() > 0.5, type: 'service' },

          // Bots (usually active)
          { name: 'Cassia', active: Math.random() > 0.1, type: 'bot' },
          { name: 'Sage', active: Math.random() > 0.2, type: 'bot' },
          { name: 'Freya', active: Math.random() > 0.2, type: 'bot' },
          { name: 'Nigella', active: Math.random() > 0.2, type: 'bot' },
          { name: 'Nyx', active: Math.random() > 0.2, type: 'bot' },
          { name: 'Anya', active: Math.random() > 0.2, type: 'bot' },
          { name: 'Casper', active: Math.random() > 0.1, type: 'bot' },
          { name: 'Pepper', active: Math.random() > 0.2, type: 'bot' },
          { name: 'Luci', active: Math.random() > 0.3, type: 'bot' },
        ];

        resolve(statuses);
      }, 100);
    });
  }

  private simulateInitialActivity() {
    const messages = [
      { entity: 'Cassia', message: 'Morning briefing scheduled for 7:00 AM', type: 'info' as const },
      { entity: 'Engine', message: 'Scheduler initialized successfully', type: 'success' as const },
      { entity: 'Dome', message: 'Open WebUI running on port 8080', type: 'success' as const },
      { entity: 'Nyx', message: 'Monitoring arXiv for new AI research', type: 'info' as const },
      { entity: 'Anya', message: 'ComfyUI workflow ready', type: 'info' as const },
      { entity: 'Portal', message: 'Telegram bot connected', type: 'success' as const },
    ];

    messages.forEach((msg, index) => {
      setTimeout(() => {
        this.addActivity({
          timestamp: new Date(),
          entity: msg.entity,
          message: msg.message,
          type: msg.type
        });
      }, index * 500);
    });

    // Add random activities periodically
    setInterval(() => {
      if (Math.random() > 0.7) {
        this.addRandomActivity();
      }
    }, 10000);
  }

  private addRandomActivity() {
    const activities = [
      { entity: 'Cassia', message: 'Updated daily schedule', type: 'info' },
      { entity: 'Sage', message: 'New research paper analyzed', type: 'success' },
      { entity: 'Freya', message: 'Workout routine generated', type: 'success' },
      { entity: 'Nigella', message: 'Dinner recipe suggested', type: 'info' },
      { entity: 'Nyx', message: 'Tech briefing prepared', type: 'info' },
      { entity: 'Anya', message: 'Playlist curated for evening', type: 'success' },
      { entity: 'Pepper', message: 'Focus session reminder', type: 'warning' },
      { entity: 'Engine', message: 'Task executed successfully', type: 'success' },
    ];

    const activity = activities[Math.floor(Math.random() * activities.length)];
    this.addActivity({
      timestamp: new Date(),
      entity: activity.entity,
      message: activity.message,
      type: activity.type as 'info' | 'success' | 'warning' | 'error'
    });
  }

  public addActivity(event: ActivityEvent) {
    this.activities.unshift(event);

    // Keep only last 50 activities
    if (this.activities.length > 50) {
      this.activities = this.activities.slice(0, 50);
    }

    this.ui.updateActivityFeed(this.activities);
  }

  public getActivities(): ActivityEvent[] {
    return this.activities;
  }
}
