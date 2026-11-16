package com.ecommerce.app.sse;

import com.ecommerce.order.event.OrderStatusChangedEvent;
import java.io.IOException;
import java.util.concurrent.CopyOnWriteArrayList;
import org.springframework.context.event.EventListener;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

/**
 * SSE (not WebSocket) for admin order-status push: one-directional
 * server->client updates over plain HTTP, simpler infra (no upgrade
 * handshake, works through standard proxies/load balancers), and the
 * admin dashboard never needs to send data back over this channel.
 * See docs/adr/0005-sse-over-websocket.md.
 */
@RestController
public class OrderStreamController {

    private final CopyOnWriteArrayList<SseEmitter> emitters = new CopyOnWriteArrayList<>();

    @GetMapping(path = "/admin/stream/orders", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter stream() {
        SseEmitter emitter = new SseEmitter(0L);
        emitters.add(emitter);
        emitter.onCompletion(() -> emitters.remove(emitter));
        emitter.onTimeout(() -> emitters.remove(emitter));
        emitter.onError(e -> emitters.remove(emitter));
        return emitter;
    }

    @EventListener
    public void onOrderStatusChanged(OrderStatusChangedEvent event) {
        for (SseEmitter emitter : emitters) {
            try {
                emitter.send(SseEmitter.event().name("order-status").data(event));
            } catch (IOException e) {
                emitters.remove(emitter);
            }
        }
    }
}
