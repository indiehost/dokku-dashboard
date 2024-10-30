import DokkuApiStatus from '../dokku-api-status'
import { DarkModeToggle } from '@/components/ui/dark-mode-toggle'
import BackButton from '@/components/shared/back-button'
import { SiGithub } from '@icons-pack/react-simple-icons';
import { Button } from "@/components/ui/button"

export default function Header() {
    return (
        <header className="flex justify-between items-center py-6">
            <BackButton />

            {/* Title with API status */}
            <div className="text-center">
                <h1 className="text-4xl font-bold">Dokku Dashboard</h1>
                <DokkuApiStatus />
            </div>

            <div className="flex gap-2">
                <DarkModeToggle />
                <Button
                    variant="outline"
                    size="icon"
                    asChild
                >
                    <a
                        href="https://github.com/indiehost/dokku-dashboard"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        <SiGithub className="h-[1.2rem] w-[1.2rem]" />
                        <span className="sr-only">GitHub repository</span>
                    </a>
                </Button>
            </div>
        </header>
    )
}