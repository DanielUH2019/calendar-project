import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { CalendarDays, Loader2, Search } from "lucide-react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"
import { z } from "zod"

import { ApiError, ReservationsService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"

const formSchema = z
  .object({
    startDate: z.string().min(1, { message: "Start date is required" }),
    endDate: z.string().min(1, { message: "End date is required" }),
    numberOfPeople: z.number().int().min(1, { message: "Must be at least 1" }),
  })
  .refine(
    (data) => {
      if (!data.startDate || !data.endDate) return true
      return data.endDate >= data.startDate
    },
    {
      message: "End date must be on or after start date",
      path: ["endDate"],
    },
  )

type FormData = z.infer<typeof formSchema>

function formatStayDate(isoDate: string) {
  const day = isoDate.split("T")[0]
  if (!day) return isoDate
  const [y, m, d] = day.split("-").map(Number)
  if (!y || !m || !d) return isoDate
  return new Date(y, m - 1, d).toLocaleDateString()
}

export const Route = createFileRoute("/_layout/reservations")({
  component: Reservations,
  head: () => ({
    meta: [
      {
        title: "Reservations - FastAPI Template",
      },
    ],
  }),
})

function Reservations() {
  const queryClient = useQueryClient()
  const reservationsQuery = useQuery({
    queryKey: ["reservations"],
    queryFn: () =>
      ReservationsService.readReservations({ skip: 0, limit: 100 }),
  })

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    defaultValues: {
      startDate: "",
      endDate: "",
      numberOfPeople: 1,
    },
  })

  const searchMutation = useMutation({
    mutationFn: (data: FormData) =>
      ReservationsService.readAvailableRooms({
        startDate: data.startDate,
        endDate: data.endDate,
        numberOfPeople: data.numberOfPeople,
      }),
    onError: (error: Error) => {
      if (error instanceof ApiError && error.body) {
        const body = error.body as { detail?: string | { msg: string }[] }
        if (typeof body.detail === "string") {
          toast.error("Search failed", { description: body.detail })
          return
        }
      }
      toast.error("Search failed", {
        description: error.message || "Something went wrong",
      })
    },
  })

  const createReservationMutation = useMutation({
    mutationFn: async ({
      roomId,
      startDate,
      endDate,
    }: {
      roomId: string
      startDate: string
      endDate: string
    }) => {
      return await ReservationsService.createReservation({
        requestBody: {
          room_id: roomId,
          start_date: startDate,
          end_date: endDate,
        },
      })
    },
    onSuccess: (_data, variables) => {
      toast.success("Reservation created", {
        description: `Held ${variables.startDate} → ${variables.endDate}`,
      })
      void queryClient.invalidateQueries({ queryKey: ["reservations"] })
      searchMutation.mutate(form.getValues())
    },
    onError: (error: Error) => {
      if (error instanceof ApiError && error.body) {
        const body = error.body as { detail?: string }
        if (typeof body.detail === "string") {
          toast.error("Could not create reservation", {
            description: body.detail,
          })
          return
        }
      }
      toast.error("Could not create reservation", {
        description: error.message || "Something went wrong",
      })
    },
  })

  const onSubmit = (data: FormData) => {
    searchMutation.mutate(data)
  }

  const rooms = searchMutation.data?.data ?? []
  const hasSearched = searchMutation.isSuccess || searchMutation.isError
  const myReservations = reservationsQuery.data?.data ?? []

  return (
    <div className="flex flex-col gap-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Reservations</h1>
        <p className="text-muted-foreground">
          Find availability by date range and party size.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <CalendarDays className="size-5" />
            Your reservations
          </CardTitle>
          <CardDescription>
            Stays you have booked, most recent first.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div data-testid="my-reservations">
            {reservationsQuery.isPending && (
              <p className="text-muted-foreground text-sm">Loading…</p>
            )}
            {reservationsQuery.isError && (
              <p className="text-destructive text-sm">
                Could not load your reservations.
              </p>
            )}
            {reservationsQuery.isSuccess && myReservations.length === 0 && (
              <p
                className="text-muted-foreground text-sm"
                data-testid="my-reservations-empty"
              >
                You do not have any reservations yet.
              </p>
            )}
            {reservationsQuery.isSuccess && myReservations.length > 0 && (
              <ul className="flex flex-col gap-2 list-none p-0 m-0">
                {myReservations.map((r) => (
                  <li
                    key={r.id}
                    className="rounded-md border px-3 py-3 text-sm"
                    data-testid="my-reservations-item"
                  >
                    <div className="font-medium">{r.room_name ?? "Room"}</div>
                    <div className="text-muted-foreground mt-1">
                      {formatStayDate(r.start_date)} –{" "}
                      {formatStayDate(r.end_date)}
                      {r.status ? (
                        <span className="text-muted-foreground">
                          {" "}
                          · {r.status}
                        </span>
                      ) : null}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Search className="size-5" />
            Search
          </CardTitle>
          <CardDescription>
            Choose your stay dates and how many people are traveling.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form
              onSubmit={form.handleSubmit(onSubmit)}
              className="flex flex-col gap-4"
            >
              <div className="grid gap-4 sm:grid-cols-2">
                <FormField
                  control={form.control}
                  name="startDate"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Start date</FormLabel>
                      <FormControl>
                        <Input type="date" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="endDate"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>End date</FormLabel>
                      <FormControl>
                        <Input type="date" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
              <FormField
                control={form.control}
                name="numberOfPeople"
                render={({ field }) => (
                  <FormItem className="max-w-xs">
                    <FormLabel>Number of people</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        min={1}
                        {...field}
                        onChange={(e) => field.onChange(e.target.valueAsNumber)}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button
                type="submit"
                className="w-fit"
                disabled={searchMutation.isPending}
              >
                {searchMutation.isPending ? (
                  <Loader2 className="mr-2 size-4 animate-spin" />
                ) : (
                  <Search className="mr-2 size-4" />
                )}
                Search
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>

      {(searchMutation.isPending || hasSearched) && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Available rooms</CardTitle>
            <CardDescription>
              Rooms available for these dates. Reserve to create a hold on a
              room you own (superusers may reserve any room).
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div data-testid="available-rooms-results">
              {searchMutation.isPending && (
                <p className="text-muted-foreground text-sm">Searching…</p>
              )}
              {searchMutation.isSuccess && rooms.length === 0 && (
                <p
                  className="text-muted-foreground text-sm"
                  data-testid="available-rooms-empty"
                >
                  No rooms match your search.
                </p>
              )}
              {searchMutation.isSuccess && rooms.length > 0 && (
                <ul className="flex flex-col gap-2 list-none p-0 m-0">
                  {rooms.map((room) => (
                    <li
                      key={room.id}
                      className="flex flex-col gap-3 rounded-md border px-3 py-3 text-sm sm:flex-row sm:items-center sm:justify-between"
                      data-testid="available-room-item"
                    >
                      <div>
                        <span className="font-medium">{room.name}</span>
                        <span className="text-muted-foreground">
                          {" "}
                          · Up to {room.max_number_of_people} people
                        </span>
                      </div>
                      <Button
                        type="button"
                        size="sm"
                        variant="secondary"
                        className="shrink-0"
                        disabled={createReservationMutation.isPending}
                        onClick={() => {
                          const { startDate, endDate } = form.getValues()
                          createReservationMutation.mutate({
                            roomId: room.id,
                            startDate,
                            endDate,
                          })
                        }}
                      >
                        Reserve
                      </Button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
