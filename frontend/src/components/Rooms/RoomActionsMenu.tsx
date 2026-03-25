import { EllipsisVertical } from "lucide-react"
import { useState } from "react"

import type { RoomPublic } from "@/client"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import DeleteRoom from "./DeleteRoom"
import EditRoom from "./EditRoom"

interface RoomActionsMenuProps {
  room: RoomPublic
}

export const RoomActionsMenu = ({ room }: RoomActionsMenuProps) => {
  const [open, setOpen] = useState(false)

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <EllipsisVertical />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <EditRoom room={room} onSuccess={() => setOpen(false)} />
        <DeleteRoom id={room.id} onSuccess={() => setOpen(false)} />
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
