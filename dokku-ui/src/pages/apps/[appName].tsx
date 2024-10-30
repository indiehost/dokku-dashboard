import { useParams } from 'react-router-dom';
import AppActions from '@/components/apps/app-actions';
import BackButton from '@/components/shared/back-button';
import AppReport from '@/components/apps/app-report';
import DomainReport from '@/components/domains/domain-report';

export default function AppDetails() {
    const { appName } = useParams();

    return (<>
        {/* Back button */}
        <BackButton />

        {/* App details */}
        <section>
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold">App details</h2>
                <AppActions appName={appName} />
            </div>
            <AppReport />
        </section>

        {/* Domains */}
        <section>
            <div className="flex justify-between items-center mb-4 mt-8">
                <h2 className="text-2xl font-bold">Domain details</h2>
            </div>
            <DomainReport />
        </section>

        {/* Logs */}
        <section>
            <div className="flex justify-between items-center mb-4 mt-8">
                <h2 className="text-2xl font-bold">Logs</h2>
            </div>
            TODO
        </section>
    </>
    );
}
