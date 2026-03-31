import { LogOut } from "lucide-react"

import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar"
import useAuth from "@/hooks/useAuth"

export function SidebarLogout() {
  const { logout } = useAuth()
  const { isMobile, setOpenMobile } = useSidebar()

  const handleLogout = () => {
    if (isMobile) {
      setOpenMobile(false)
    }
    logout()
  }

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <SidebarMenuButton
          tooltip="Log out"
          data-testid="logout-button"
          onClick={handleLogout}
        >
          <LogOut className="size-4" />
          <span>Log out</span>
        </SidebarMenuButton>
      </SidebarMenuItem>
    </SidebarMenu>
  )
}
