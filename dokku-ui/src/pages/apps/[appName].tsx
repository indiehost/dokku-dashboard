import { useParams } from 'react-router-dom';
import AppActions from '@/components/apps/app-actions';
import AppReport from '@/components/apps/app-report';
import DomainReport from '@/components/domains/domain-report';
import AppLogs from '@/components/logs/app-logs';
import ProcessReport from '@/components/processes/process-report';

export default function AppDetails() {
    const { appName } = useParams();

    return (<>

        {/* App details */}
        <section>
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold">App details</h2>
                <AppActions appName={appName} />
            </div>
            <AppReport />
        </section>

        {/* Processes */}
        <section>
            <div className="flex justify-between items-center mb-4 mt-8">
                <h2 className="text-2xl font-bold">Process details</h2>
            </div>
            <ProcessReport />
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

            <AppLogs appName={appName} />
        </section>

        {/* Env vars */}
        <section>
            <div className="flex justify-between items-center mb-4 mt-8">
                <h2 className="text-2xl font-bold">Environment variables</h2>
            </div>
            TODO
        </section>

    </>
    );
}
