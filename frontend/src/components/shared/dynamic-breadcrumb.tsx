"use client"

import * as React from "react"
import {useRouter, usePathname} from "next/navigation"
import {Home} from "lucide-react"
import {cn} from "@/lib/utils"
import {
    Breadcrumb,
    BreadcrumbItem, BreadcrumbLink,
    BreadcrumbList,
    BreadcrumbPage,
    BreadcrumbSeparator
} from "@/components/ui/breadcrumb";

interface BreadcrumbItemConfig {
    label: string
    href: string
    isCurrent?: boolean
}

interface DynamicBreadcrumbProps {
    homeLabel?: string
    className?: string
    separator?: React.ReactNode
    showHome?: boolean
    maxItems?: number
    customLabels?: Record<string, string>
}

function DynamicBreadcrumb({
                               homeLabel = "Home",
                               className,
                               separator,
                               showHome = true,
                               maxItems = 5,
                               customLabels = {},
                               ...props
                           }: DynamicBreadcrumbProps & React.ComponentProps<"nav">) {

    const router = useRouter()
    const pathname = usePathname()

    const generateBreadcrumbItems = (): BreadcrumbItemConfig[] => {
        if (!pathname) return []

        const cleanPathname = pathname.split('?')[0].split('#')[0]
        const segments = cleanPathname.split('/').filter(Boolean)

        const items: BreadcrumbItemConfig[] = []

        if (showHome) {
            items.push({
                label: homeLabel,
                href: '/',
                isCurrent: segments.length === 0
            })
        }

        let accumulatedPath = ''
        segments.forEach((segment, index) => {
            accumulatedPath += `/${segment}`

            const label = customLabels[segment]
                || customLabels[accumulatedPath]
                || formatSegmentLabel(segment)

            items.push({
                label,
                href: accumulatedPath,
                isCurrent: index === segments.length - 1
            })
        })

        return items
    }

    const formatSegmentLabel = (segment: string): string => {
        return segment
            .replace(/[-_]/g, ' ')
            .replace(/\b\w/g, char => char.toUpperCase())
            .replace(/\b(a|e|o|de|do|da|dos|das|em|por)\b/gi, match => match.toLowerCase())
    }

    const shouldDisplaySegment = (label: string): boolean => {
        // remove espaços para validação
        const plain = label.replace(/\s+/g, "")

        // mais de 10 letras
        if (plain.length > 10) return false

        // apenas números
        if (/^\d+$/.test(plain)) return false

        return true
    }

    const getTruncatedItems = (items: BreadcrumbItemConfig[]): BreadcrumbItemConfig[] => {
        if (items.length <= maxItems) return items

        const firstItem = items[0]
        const lastTwoItems = items.slice(-2)
        const middleItems = items.slice(1, -2)

        return [
            firstItem,
            {
                label: "...",
                href: middleItems[middleItems.length - 1]?.href || '',
                isCurrent: false
            },
            ...lastTwoItems
        ]
    }

    // 1) gera items
    let breadcrumbItems = generateBreadcrumbItems()

    // 2) filtra os segmentos
    breadcrumbItems = breadcrumbItems.filter(item => shouldDisplaySegment(item.label))

    // 3) aplica truncamento
    breadcrumbItems = getTruncatedItems(breadcrumbItems)

    if (breadcrumbItems.length === 0) return null

    return (
        <Breadcrumb
            className={cn("mb-6", className)}
            aria-label="Navegação estrutural"
            {...props}
        >
            <BreadcrumbList>
                {breadcrumbItems.map((item, index) => (
                    <div className="flex items-center gap-2" key={item.href}>
                        <BreadcrumbItem className="flex items-center">
                            {item.isCurrent ? (
                                <BreadcrumbPage className="flex gap-1 items-center">
                                    {index === 0 && showHome && <Home className="size-4" />}
                                    {item.label}
                                </BreadcrumbPage>
                            ) : (
                                <BreadcrumbLink
                                    href={item.href}
                                    className="flex gap-1 items-center hover:text-foreground/80 transition-colors"
                                    onClick={e => {
                                        e.preventDefault()
                                        router.push(item.href)
                                    }}
                                >
                                    {index === 0 && showHome && <Home className="size-4" />}
                                    {item.label}
                                </BreadcrumbLink>
                            )}
                        </BreadcrumbItem>

                        {index < breadcrumbItems.length - 1 && (
                            <BreadcrumbSeparator>
                                {separator}
                            </BreadcrumbSeparator>
                        )}
                    </div>
                ))}
            </BreadcrumbList>
        </Breadcrumb>
    )
}

export {
    DynamicBreadcrumb
}
