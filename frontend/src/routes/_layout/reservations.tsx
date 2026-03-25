import { zodResolver } from "@hookform/resolvers/zod"
import { createFileRoute } from "@tanstack/react-router"
import { Search } from "lucide-react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"
import { z } from "zod"

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
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    defaultValues: {
      startDate: "",
      endDate: "",
      numberOfPeople: 1,
    },
  })

  const onSubmit = (_data: FormData) => {
    toast.info("Search is not connected yet", {
      description:
        "Reservation search will be available once the backend is wired up.",
    })
  }

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
              <Button type="submit" className="w-fit">
                <Search className="mr-2 size-4" />
                Search
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  )
}
