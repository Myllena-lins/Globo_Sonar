import Link from "next/link"
import {Button} from "@/components/ui/button"
import ThemeToggler from "@/components/shared/theme-toggler";

export default function Header() {
    return (
        <header className="sticky top-0 z-50 w-full backdrop-blur ">
            <div className="py-4">
                <div className="flex items-center justify-between">
                    <Link href="/" className="text-xl font-bold">
                        S<span className="text-primary">O</span>NAR
                    </Link>
                    <nav className="hidden md:flex items-center gap-6">
                        <Link href="/" className="text-sm transition-colors hover:text-primary">
                            Enviar Arquivo
                        </Link>
                        <Link href="/" className="text-sm transition-colors hover:text-primary">
                            Sobre nós
                        </Link>
                    </nav>
                    <div className="flex items-center gap-4">
                        <ThemeToggler/>
                    </div>
                </div>
            </div>
        </header>
    )
}