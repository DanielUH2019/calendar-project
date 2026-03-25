import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Search } from "lucide-react"
import { Suspense } from "react"

import { RoomsService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import PendingRooms from "@/components/Pending/PendingRooms"
import AddRoom from "@/components/Rooms/AddRoom"
import { columns } from "@/components/Rooms/columns"

function getRoomsQueryOptions() {
  return {
    queryFn: () => RoomsService.readRooms({ skip: 0, limit: 100 }),
    queryKey: ["rooms"],
  }
}

export const Route = createFileRoute("/_layout/rooms")({
  component: Rooms,
  head: () => ({
    meta: [
      {
        title: "Rooms - FastAPI Template",
      },
    ],
  }),
})

function RoomsTableContent() {
  const { data: rooms } = useSuspenseQuery(getRoomsQueryOptions())

  if (rooms.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <Search className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">You don't have any rooms yet</h3>
        <p className="text-muted-foreground">Add a new room to get started</p>
      </div>
    )
  }

  return <DataTable columns={columns} data={rooms.data} />
}

function RoomsTable() {
  return (
    <Suspense fallback={<PendingRooms />}>
      <RoomsTableContent />
    </Suspense>
  )
}

function Rooms() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Rooms</h1>
          <p className="text-muted-foreground">Create and manage your rooms</p>
        </div>
        <AddRoom />
      </div>
      <RoomsTable />
    </div>
  )
}
