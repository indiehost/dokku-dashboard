import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';

export default function BackButton() {
    const navigate = useNavigate();
    const location = useLocation();

    return (
        <div className="flex justify-between items-center">
            <Button variant="outline" onClick={() => navigate(-1)} className={location.pathname === '/' ? 'invisible' : ''}>
                <ArrowLeft className="w-4 h-4" />
            </Button>
        </div>
    )
}