package com.bank.updg.updg_system.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_system.model.entity.Meeting;
import com.bank.updg.updg_system.service.MeetingService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * F-1101: Meeting management.
 */
@RestController
@RequestMapping("/api/system/meeting")
@RequiredArgsConstructor
public class MeetingController {

    private final MeetingService meetingService;

    @PostMapping
    public ApiResponse<Meeting> create(@RequestBody Meeting meeting) {
        return ApiResponse.success(meetingService.createMeeting(meeting));
    }

    @GetMapping("/project/{projectId}")
    public ApiResponse<List<Meeting>> getByProject(@PathVariable String projectId) {
        return ApiResponse.success(meetingService.getByProjectId(projectId));
    }

    @PostMapping("/{id}/complete")
    public ApiResponse<Void> complete(@PathVariable String id,
                                      @RequestBody Map<String, String> body) {
        meetingService.completeMeeting(id, body.get("minutes"));
        return ApiResponse.success();
    }

    @PostMapping("/{id}/cancel")
    public ApiResponse<Void> cancel(@PathVariable String id) {
        meetingService.cancelMeeting(id);
        return ApiResponse.success();
    }
}
