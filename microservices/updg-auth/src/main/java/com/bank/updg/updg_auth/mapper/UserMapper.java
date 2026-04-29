package com.bank.updg.updg_auth.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.bank.updg.updg_auth.model.entity.User;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface UserMapper extends BaseMapper<User> {
}
