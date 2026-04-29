package com.bank.updg.updg_resource.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_resource.model.entity.LeaveRequest;
import com.bank.updg.updg_resource.service.LeaveRequestService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * F-1103: Leave request management.
 */
@RestController
@RequestMapping("/api/resource/leave")
@RequiredArgsConstructor
public class LeaveRequestController {

    private final LeaveRequestService leaveRequestService;

    @PostMapping
    public ApiResponse<LeaveRequest> submit(@RequestBody LeaveRequest request) {
        return ApiResponse.success(leaveRequestService.submitRequest(request));
    }

    @GetMapping("/staff/{staffId}")
    public ApiResponse<List<LeaveRequest>> getByStaff(@PathVariable String staffId) {
        return ApiResponse.success(leaveRequestService.getByStaffId(staffId));
    }

    @GetMapping("/pending")
    public ApiResponse<List<LeaveRequest>> getPending() {
        return ApiResponse.success(leaveRequestService.getPending());
    }

    @PostMapping("/{id}/approve")
    public ApiResponse<Void> approve(@PathVariable String id,
                                     @RequestBody Map<String, String> body) {
        leaveRequestService.approveRequest(id, body.get("approvedBy"));
        return ApiResponse.success();
    }

    @PostMapping("/{id}/reject")
    public ApiResponse<Void> reject(@PathVariable String id,
                                    @RequestBody Map<String, String> body) {
        leaveRequestService.rejectRequest(id, body.get("approvedBy"));
        return ApiResponse.success();
    }
}
