import { AboutHero } from './AboutHero';
import { AboutStory } from './AboutStory';
import { AboutMission } from './AboutMission';
import { AboutValues } from './AboutValues';
import { AboutTeam } from './AboutTeam';

export function AboutPage() {
  return (
    <div className="space-y-4">
      <AboutHero />
      <AboutStory />
      <AboutMission />
      <AboutValues />
      <AboutTeam />
    </div>
  );
}
