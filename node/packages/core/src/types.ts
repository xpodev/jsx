import type { SocketOptions, ManagerOptions } from "socket.io-client";

export interface SeamlessOptions {
  socketOptions?: Partial<ManagerOptions & SocketOptions>;
  /**
   * A function that serializes the event object before sending it to the server
   * The default behavior is to return the event object as is
   *
   * @param originalEvent The original event object
   * @param outEvent The event object that is constructed by `serializeEventObject`
   * @returns The object that will be sent to the server
   */
  eventObjectTransformer?: (originalEvent: Event, outEvent: any) => any;
}

export interface OutEvent<T = any> {
  type: string;
  data: T;
}

export type Primitive = string | number | boolean | null;

export interface SeamlessElement {
  type: string;
  props: Record<string, any>;
  children: Array<SeamlessElement | Primitive> | null;
}