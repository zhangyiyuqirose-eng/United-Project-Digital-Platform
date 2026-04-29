package com.bank.updg.updg_resource.controller;

import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_resource.model.entity.ResourceOutsourcing;
import com.bank.updg.updg_resource.service.ResourceOutsourcingService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/resource/outsourcing")
@RequiredArgsConstructor
public class ResourceOutsourcingController {

    private final ResourceOutsourcingService outsourcingService;

    @GetMapping("/pool/{pool}")
    public ApiResponse listByPool(@PathVariable String pool,
                                  @RequestParam(defaultValue = "1") int page,
                                  @RequestParam(defaultValue = "20") int size) {
        return ApiResponse.success(outsourcingService.listByPool(pool, page, size));
    }

    @GetMapping("/{staffId}")
    public ApiResponse getById(@PathVariable String staffId) {
        return ApiResponse.success(outsourcingService.getById(staffId));
    }

    @PostMapping
    public ApiResponse add(@RequestBody ResourceOutsourcing resource) {
        outsourcingService.add(resource);
        return ApiResponse.success("添加成功");
    }

    @PutMapping("/{staffId}")
    public ApiResponse update(@PathVariable String staffId, @RequestBody ResourceOutsourcing resource) {
        resource.setStaffId(staffId);
        outsourcingService.update(resource);
        return ApiResponse.success("更新成功");
    }

    @PostMapping("/{staffId}/exit")
    public ApiResponse exitStaff(@PathVariable String staffId) {
        outsourcingService.exitStaff(staffId);
        return ApiResponse.success("离场成功");
    }

    @GetMapping("/skills/{skill}")
    public ApiResponse listBySkill(@PathVariable String skill) {
        return ApiResponse.success(outsourcingService.listActiveBySkill(skill));
    }
}
